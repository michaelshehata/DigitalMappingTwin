# Full pipeline for Random Forest and XGBoost training


import os
import time
import warnings

import numpy as np
import pandas as pd
import rasterio

from sklearn.ensemble import RandomForestClassifier
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.model_selection import StratifiedShuffleSplit
from xgboost import XGBClassifier

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    cohen_kappa_score,
    confusion_matrix,
    classification_report
)

warnings.filterwarnings("ignore")


# CONFIG


DATA_DIR    = "processed_data"
RESULTS_DIR = "model_results"

os.makedirs(RESULTS_DIR, exist_ok=True)

SNAPSHOT_YEARS = [1985, 1995, 2005, 2015, 2024]

# Stratified split ratios applied independently per year.
# Using StratifiedShuffleSplit instead of sequential block slicing
# ensures minority classes (Water ~0.4%, Sparse ~0.1%) appear in
# every subset rather than clustering in a single spatial block.
TRAIN_RATIO = 0.70
VAL_RATIO   = 0.20
# TEST_RATIO  = 0.10 (remainder)

# Set to True to apply SMOTE oversampling on the training set after
# splitting. Useful if class_weight='balanced' alone is insufficient.
# Requires: pip install imbalanced-learn
USE_SMOTE = False


# LOAD RASTER


def load_raster(path):
    with rasterio.open(path) as src:
        data = src.read()
    return data.astype(np.float32)


# LOAD FEATURES FOR ONE YEAR


def build_feature_stack(year):

    rgb       = load_raster(f"{DATA_DIR}/rgb_{year}.tif")
    ndvi      = load_raster(f"{DATA_DIR}/ndvi_{year}.tif")
    temp      = load_raster(f"{DATA_DIR}/temperature_{year}.tif")
    elevation = load_raster(f"{DATA_DIR}/elevation.tif")
    water     = load_raster(f"{DATA_DIR}/distance_to_water.tif")
    labels    = load_raster(f"{DATA_DIR}/labels_{year}.tif")[0]

    
    # Population mapping (nearest available snapshot)
    

    if year <= 2005:
        population = load_raster(f"{DATA_DIR}/population_2000.tif")
    elif year <= 2015:
        population = load_raster(f"{DATA_DIR}/population_2010.tif")
    else:
        population = load_raster(f"{DATA_DIR}/population_2020.tif")

    
    # STACK FEATURES
    

    feature_list = []

    for i in range(rgb.shape[0]):
        feature_list.append(rgb[i])

    for i in range(ndvi.shape[0]):
        feature_list.append(ndvi[i])

    for i in range(temp.shape[0]):
        feature_list.append(temp[i])

    for i in range(population.shape[0]):
        feature_list.append(population[i])

    feature_list.append(elevation[0])
    feature_list.append(water[0])

    X = np.stack(feature_list, axis=-1)

    return X, labels


# CLASS DISTRIBUTION HELPER


CLASS_NAMES = {
    0: "Vegetation",
    1: "Agricultural",
    2: "Urban",
    3: "Water",
    4: "Sparse"
}

def print_class_distribution(y, label):
    total = len(y)
    classes, counts = np.unique(y, return_counts=True)
    print(f"  {label} class distribution:")
    for c, n in zip(classes, counts):
        name = CLASS_NAMES.get(int(c), f"Class {c}")
        print(f"    {name:15s} : {n:>8,}  ({100.0 * n / total:.2f}%)")


# PER-YEAR STRATIFIED SPLIT
#
# Each snapshot year is split independently using
# StratifiedShuffleSplit before concatenation. This preserves the
# original spatial blocking rationale (every year contributes
# proportionally to all three subsets) while additionally ensuring
# that minority classes — Water (~0.4%) and Sparse (~0.1%) — are
# represented in the validation and test subsets rather than
# concentrating in whichever spatial block happens to contain them.
#
# The original sequential block split assigned pixels 0..train_end to
# training, train_end..val_end to validation, and the remainder to
# test. Since land cover classes are spatially autocorrelated, rare
# classes that cluster in a single geographic region (e.g. Water near
# the river Wensum) could fall almost entirely in one subset, starving
# the others of any signal for those classes and producing the very
# low macro F1 / near-zero per-class recall observed in the original
# results.


print("\nLoading and splitting datasets per year...\n")

X_train_parts = []
X_val_parts   = []
X_test_parts  = []

y_train_parts = []
y_val_parts   = []
y_test_parts  = []

for year in SNAPSHOT_YEARS:

    print(f"Processing year: {year}")

    X, y = build_feature_stack(year)

    h, w, c = X.shape

    X = X.reshape(-1, c)
    y = y.reshape(-1)

    
    # Remove invalid labels (255 = NoData)
    

    valid_mask = (y >= 0) & (y != 255)
    X = X[valid_mask]
    y = y[valid_mask].astype(np.int32)

    n = len(y)

    
    # Stratified split: train vs (val + test)
    # StratifiedShuffleSplit guarantees that every class
    # present in the full dataset appears in both the
    # training subset and the held-out pool, in proportion.
    

    sss_traintest = StratifiedShuffleSplit(
        n_splits=1,
        test_size=(1.0 - TRAIN_RATIO),
        random_state=42
    )
    train_idx, temp_idx = next(sss_traintest.split(X, y))

    X_temp = X[temp_idx]
    y_temp = y[temp_idx]

    
    # Stratified split: val vs test from the held-out pool.
    # VAL_RATIO is expressed as a fraction of the full
    # dataset; here we convert it to a fraction of temp.
    

    val_fraction_of_temp = VAL_RATIO / (1.0 - TRAIN_RATIO)

    sss_valtest = StratifiedShuffleSplit(
        n_splits=1,
        test_size=(1.0 - val_fraction_of_temp),
        random_state=42
    )
    val_idx, test_idx = next(sss_valtest.split(X_temp, y_temp))

    X_train_parts.append(X[train_idx])
    X_val_parts.append(X_temp[val_idx])
    X_test_parts.append(X_temp[test_idx])

    y_train_parts.append(y[train_idx])
    y_val_parts.append(y_temp[val_idx])
    y_test_parts.append(y_temp[test_idx])

    print(f"  Year {year} — train: {len(train_idx):,} | "
          f"val: {len(val_idx):,} | "
          f"test: {len(test_idx):,}")


# CONCATENATE SPLITS ACROSS ALL YEARS


X_train = np.concatenate(X_train_parts, axis=0)
X_val   = np.concatenate(X_val_parts,   axis=0)
X_test  = np.concatenate(X_test_parts,  axis=0)

y_train = np.concatenate(y_train_parts, axis=0)
y_val   = np.concatenate(y_val_parts,   axis=0)
y_test  = np.concatenate(y_test_parts,  axis=0)

print(f"\nFinal dataset sizes:")
print(f"  Train : {len(y_train):,}")
print(f"  Val   : {len(y_val):,}")
print(f"  Test  : {len(y_test):,}")
print(f"  Features: {X_train.shape[1]}")

print()
print_class_distribution(y_train, "Train")
print()
print_class_distribution(y_val,   "Val  ")
print()
print_class_distribution(y_test,  "Test ")


# OPTIONAL SMOTE OVERSAMPLING
#
# Applied only to X_train / y_train after the split so that
# no synthetic samples leak into the validation or test sets.
# SMOTETomek combines SMOTE oversampling of minority classes
# with Tomek link removal to clean ambiguous majority-class
# samples near the decision boundary.


if USE_SMOTE:
    print("\nApplying SMOTETomek oversampling to training set...")
    from imblearn.combine import SMOTETomek
    resampler = SMOTETomek(random_state=42)
    X_train, y_train = resampler.fit_resample(X_train, y_train)
    print(f"  Resampled train size: {len(y_train):,}")
    print()
    print_class_distribution(y_train, "Train (after SMOTE)")


# MODEL CONFIGS


rf_configs = [
    {
        "name": "RF_1",
        "n_estimators": 100,
        "max_depth": 15,
        "min_samples_split": 2
    },
    {
        "name": "RF_2",
        "n_estimators": 200,
        "max_depth": 20,
        "min_samples_split": 5
    },
    {
        "name": "RF_3",
        # max_depth=None means fully grown trees (unconstrained depth).
        # This matches the report's Table 6 which specifies None for RF_3.
        "n_estimators": 300,
        "max_depth": None,
        "min_samples_split": 10
    }
]

xgb_configs = [
    {
        "name": "XGB_1",
        "n_estimators": 100,
        "max_depth": 6,
        "learning_rate": 0.10
    },
    {
        "name": "XGB_2",
        "n_estimators": 200,
        "max_depth": 8,
        "learning_rate": 0.05
    },
    {
        "name": "XGB_3",
        "n_estimators": 300,
        "max_depth": 10,
        "learning_rate": 0.03
    }
]


# EVALUATION FUNCTION


def evaluate_model(model_name, model, X_eval, y_eval):

    start_time = time.time()
    predictions = model.predict(X_eval)
    prediction_time = time.time() - start_time

    accuracy  = accuracy_score(y_eval, predictions)
    macro_f1  = f1_score(y_eval, predictions, average="macro")
    precision = precision_score(y_eval, predictions, average="macro", zero_division=0)
    recall    = recall_score(y_eval, predictions, average="macro", zero_division=0)
    kappa     = cohen_kappa_score(y_eval, predictions)
    cm        = confusion_matrix(y_eval, predictions)
    report    = classification_report(
        y_eval, predictions,
        target_names=[CLASS_NAMES[i] for i in sorted(CLASS_NAMES)],
        digits=4
    )

    pd.DataFrame(cm).to_csv(
        f"{RESULTS_DIR}/{model_name}_confusion_matrix.csv", index=False
    )

    with open(f"{RESULTS_DIR}/{model_name}_classification_report.txt", "w") as f:
        f.write(report)

    return {
        "model":                    model_name,
        "accuracy":                 accuracy,
        "macro_f1":                 macro_f1,
        "precision":                precision,
        "recall":                   recall,
        "kappa":                    kappa,
        "prediction_time_seconds":  prediction_time
    }


# TRAINING LOOP
#
# Workflow:
#   1. Train each configuration on X_train.
#   2. Evaluate on X_val to select the best config per
#      model family (highest macro F1).
#   3. Re-evaluate the winning config on X_test for the
#      final unbiased reported metrics.
#
# The test set is accessed exactly once per model family,
# only after the best configuration has been identified
# via the validation set. This prevents the test set from
# influencing any model selection decisions.


val_results  = []
test_results = []

NUM_CLASSES = len(np.unique(np.concatenate([y_train, y_val, y_test])))

# Pre-compute sample weights for XGBoost once, based on training labels.
# compute_sample_weight('balanced') assigns each sample a weight
# inversely proportional to its class frequency, so the gradient
# updates from Water and Sparse samples are amplified to match those
# of the dominant Agricultural class.
xgb_sample_weights = compute_sample_weight(class_weight="balanced", y=y_train)


# Random Forest



print("TRAINING RANDOM FOREST MODELS")


best_rf_val_f1  = -1
best_rf_model   = None
best_rf_name    = None
best_rf_time    = None

for config in rf_configs:

    print(f"Training {config['name']}...")

    start_train = time.time()

    # class_weight='balanced' scales each class's contribution to the
    # Gini impurity calculation in every tree by the inverse of its
    # frequency. This means a split that correctly separates a Water
    # pixel receives the same impurity-reduction credit as one that
    # correctly separates ~160 Agricultural pixels (reflecting the
    # ~0.4% vs ~65% frequency ratio). Without this, the forest
    # effectively ignores minority classes because the impurity gain
    # from splitting them is negligible relative to the majority class.
    model = RandomForestClassifier(
        n_estimators=config["n_estimators"],
        max_depth=config["max_depth"],
        min_samples_split=config["min_samples_split"],
        class_weight="balanced",
        n_jobs=-1,
        random_state=42
    )

    model.fit(X_train, y_train)
    train_time = time.time() - start_train

    # Evaluate on validation set for model selection
    val_metrics = evaluate_model(config["name"] + "_val", model, X_val, y_val)
    val_metrics["train_time_seconds"] = train_time
    val_metrics["split"] = "validation"
    val_results.append(val_metrics)

    print(f"  Val macro F1: {val_metrics['macro_f1']:.4f} | "
          f"Accuracy: {val_metrics['accuracy']:.4f} | "
          f"Train time: {train_time:.1f}s")

    # Track best RF config by validation macro F1
    if val_metrics["macro_f1"] > best_rf_val_f1:
        best_rf_val_f1 = val_metrics["macro_f1"]
        best_rf_model  = model
        best_rf_name   = config["name"]
        best_rf_time   = train_time

    # Save feature importances for every config
    pd.DataFrame({
        "feature_index": np.arange(len(model.feature_importances_)),
        "importance":    model.feature_importances_
    }).sort_values("importance", ascending=False).to_csv(
        f"{RESULTS_DIR}/{config['name']}_feature_importance.csv", index=False
    )

# Final test evaluation for best RF only
print(f"\nBest RF config: {best_rf_name} (val macro F1: {best_rf_val_f1:.4f})")
print(f"Evaluating {best_rf_name} on test set...")

test_metrics = evaluate_model(best_rf_name + "_test", best_rf_model, X_test, y_test)
test_metrics["train_time_seconds"] = best_rf_time
test_metrics["split"] = "test"
test_results.append(test_metrics)

print(f"  Test macro F1: {test_metrics['macro_f1']:.4f} | "
      f"Accuracy: {test_metrics['accuracy']:.4f}")


# XGBoost



print("TRAINING XGBOOST MODELS")


best_xgb_val_f1 = -1
best_xgb_model  = None
best_xgb_name   = None
best_xgb_time   = None

for config in xgb_configs:

    print(f"Training {config['name']}...")

    start_train = time.time()

    # XGBoost does not accept class_weight directly. Instead,
    # per-sample weights are passed to model.fit() via the
    # sample_weight argument. These were pre-computed above using
    # compute_sample_weight('balanced') so that the boosting gradient
    # treats each class equally regardless of pixel frequency.
    model = XGBClassifier(
        n_estimators=config["n_estimators"],
        max_depth=config["max_depth"],
        learning_rate=config["learning_rate"],
        objective="multi:softmax",
        num_class=NUM_CLASSES,
        eval_metric="mlogloss",
        tree_method="hist",
        random_state=42
    )

    model.fit(X_train, y_train, sample_weight=xgb_sample_weights)
    train_time = time.time() - start_train

    # Evaluate on validation set for model selection
    val_metrics = evaluate_model(config["name"] + "_val", model, X_val, y_val)
    val_metrics["train_time_seconds"] = train_time
    val_metrics["split"] = "validation"
    val_results.append(val_metrics)

    print(f"  Val macro F1: {val_metrics['macro_f1']:.4f} | "
          f"Accuracy: {val_metrics['accuracy']:.4f} | "
          f"Train time: {train_time:.1f}s")

    if val_metrics["macro_f1"] > best_xgb_val_f1:
        best_xgb_val_f1 = val_metrics["macro_f1"]
        best_xgb_model  = model
        best_xgb_name   = config["name"]
        best_xgb_time   = train_time

# Final test evaluation for best XGB only
print(f"\nBest XGB config: {best_xgb_name} (val macro F1: {best_xgb_val_f1:.4f})")
print(f"Evaluating {best_xgb_name} on test set...")

test_metrics = evaluate_model(best_xgb_name + "_test", best_xgb_model, X_test, y_test)
test_metrics["train_time_seconds"] = best_xgb_time
test_metrics["split"] = "test"
test_results.append(test_metrics)

print(f"  Test macro F1: {test_metrics['macro_f1']:.4f} | "
      f"Accuracy: {test_metrics['accuracy']:.4f}")


# SAVE RESULTS


# All validation results (all configs, for transparency)
pd.DataFrame(val_results).to_csv(
    f"{RESULTS_DIR}/validation_results.csv", index=False
)

# Final test results (best config per family only)
pd.DataFrame(test_results).to_csv(
    f"{RESULTS_DIR}/test_results.csv", index=False
)

# Combined for convenience
all_results = pd.DataFrame(val_results + test_results)
all_results.to_csv(
    f"{RESULTS_DIR}/all_model_results.csv", index=False
)


print("ALL TRAINING COMPLETE")

print(f"\nValidation results : {RESULTS_DIR}/validation_results.csv")
print(f"Test results       : {RESULTS_DIR}/test_results.csv")
print(f"Combined results   : {RESULTS_DIR}/all_model_results.csv")