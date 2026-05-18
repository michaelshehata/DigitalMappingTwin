import numpy as np
import joblib
import json
import os

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, f1_score, roc_auc_score,
    precision_recall_curve, auc, confusion_matrix
)
from xgboost import XGBClassifier

import sys
sys.path.append(os.path.abspath(".."))

from scripts.load_data import load_all_data

np.random.seed(6001)


# EXPERIMENT NAME
experiment_name = "XGB-3"


# OUTPUT DIRECTORY
output_dir = "model_output/hyperparameter_tuning/xgboost"

os.makedirs(output_dir, exist_ok=True)

X, y, _ = load_all_data()

X_flat = X.reshape(-1, X.shape[-1])
y_flat = y.flatten()

mask = (y_flat >= 0)
X_flat = X_flat[mask]
y_flat = y_flat[mask]

feature_names = ["NDVI", "Population", "Temperature", "Elevation", "Distance_to_Water", "Landcover"]

print("Dataset shape:", X_flat.shape)
print("Features:", feature_names)
print("Class distribution:")
unique, counts = np.unique(y_flat, return_counts=True)
for u, c in zip(unique, counts):
    print(f"  Class {u}: {c}")

sample_size = min(50000, len(X_flat))
indices = np.random.choice(len(X_flat), sample_size, replace=False)
X_sample = X_flat[indices]
y_sample = y_flat[indices]

X_train, X_temp, y_train, y_temp = train_test_split(
    X_sample, y_sample, test_size=0.3, stratify=y_sample, random_state=6001
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=2/3, stratify=y_temp, random_state=6001
)

assert abs(X_train.shape[0] / len(X_sample) - 0.7) < 0.01
assert abs(X_val.shape[0] / len(X_sample) - 0.1) < 0.01
assert abs(X_test.shape[0] / len(X_sample) - 0.2) < 0.01

print(f"\nTrain: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")

scale_pos_weight = len(y_train[y_train == 0]) / len(y_train[y_train == 1])

model = XGBClassifier(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.1,
    scale_pos_weight=8,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="logloss",
    n_jobs=-1,
    random_state=6001
)

print("\nTraining XGBoost...")
model.fit(X_train, y_train)

y_val_prob = model.predict_proba(X_val)[:, 1]
y_test_prob = model.predict_proba(X_test)[:, 1]

thresholds = np.arange(0.1, 0.9, 0.05)
best_threshold = 0.5
best_f1 = 0

for thresh in thresholds:
    y_val_pred_temp = (y_val_prob > thresh).astype(int)
    f1_temp = f1_score(y_val, y_val_pred_temp)
    if f1_temp > best_f1:
        best_f1 = f1_temp
        best_threshold = thresh

print(f"Optimal threshold (validation F1): {best_threshold:.2f}")

y_val_pred = (y_val_prob > best_threshold).astype(int)
y_test_pred = (y_test_prob > best_threshold).astype(int)

val_auc = roc_auc_score(y_val, y_val_prob)
test_auc = roc_auc_score(y_test, y_test_prob)
test_f1 = f1_score(y_test, y_test_pred)

precision, recall, _ = precision_recall_curve(y_test, y_test_prob)
pr_auc = auc(recall, precision)

tn, fp, fn, tp = confusion_matrix(y_test, y_test_pred).ravel()

sensitivity = tp / (tp + fn)
specificity = tn / (tn + fp)

precision_score = tp / (tp + fp) if (tp + fp) > 0 else 0

print(f"\nValidation AUROC: {val_auc:.4f}")
print(f"\nTest Metrics:")
print(f"  AUROC: {test_auc:.4f}")
print(f"  PR-AUC: {pr_auc:.4f}")
print(f"  F1-Score: {test_f1:.4f}")
print(f"  Precision: {precision_score:.4f}")
print(f"  Recall: {sensitivity:.4f}")
print(f"  Specificity: {specificity:.4f}")

print(f"\nClassification Report:")
print(classification_report(y_test, y_test_pred))

joblib.dump(
    model,
    os.path.join(output_dir, f"{experiment_name}.pkl")
)

metrics = {
    "experiment_name": experiment_name,
    "model": "xgboost",

    "optimal_threshold": float(best_threshold),

    "val_auroc": float(val_auc),

    "test_auroc": float(test_auc),
    "test_pr_auc": float(pr_auc),
    "test_f1": float(test_f1),

    "test_precision": float(precision_score),
    "test_recall": float(sensitivity),
    "test_specificity": float(specificity),

    "true_negatives": int(tn),
    "false_positives": int(fp),
    "false_negatives": int(fn),
    "true_positives": int(tp),

    "n_estimators": model.get_params().get("n_estimators"),
    "max_depth": model.get_params().get("max_depth"),
    "learning_rate": model.get_params().get("learning_rate"),
    "scale_pos_weight": model.get_params().get("scale_pos_weight"),

    "feature_names": feature_names,
    "feature_importance": model.feature_importances_.tolist()
}

with open(
    os.path.join(output_dir, f"{experiment_name}_metrics.json"),
    "w"
) as f:
    json.dump(metrics, f, indent=2)

print("\nTraining complete, models saved")