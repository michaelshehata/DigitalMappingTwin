import numpy as np
import joblib
import json
import os

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, f1_score, roc_auc_score,
    precision_recall_curve, auc, confusion_matrix
)

import sys
sys.path.append(os.path.abspath(".."))

from scripts.load_data import load_all_data

np.random.seed(42)

X, y, _ = load_all_data()

X_flat = X.reshape(-1, X.shape[-1])
y_flat = y.flatten()

mask = (y_flat >= 0)
X_flat = X_flat[mask]
y_flat = y_flat[mask]

feature_names = ["NDVI", "Population", "Temperature", "Elevation", "Distance_to_Water"]

print("Dataset shape:", X_flat.shape)
print("Features:", feature_names)
print("Class distribution:")
unique, counts = np.unique(y_flat, return_counts=True)
for u, c in zip(unique, counts):
    print(f"  Class {u}: {c}")

sample_size = 200000
indices = np.random.choice(len(X_flat), sample_size, replace=False)
X_sample = X_flat[indices]
y_sample = y_flat[indices]

X_train, X_temp, y_train, y_temp = train_test_split(
    X_sample, y_sample, test_size=0.3, stratify=y_sample, random_state=42
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=2/3, stratify=y_temp, random_state=42
)

print(f"\nTrain: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")

model = RandomForestClassifier(
    n_estimators=150,
    max_depth=30,
    n_jobs=-1,
    random_state=42,
    class_weight={0: 1, 1: 5}
)

print("\nTraining RandomForest...")
model.fit(X_train, y_train)

y_val_prob = model.predict_proba(X_val)[:, 1]
y_test_prob = model.predict_proba(X_test)[:, 1]

# Threshold optimization on validation set
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

print(f"\nValidation AUROC: {val_auc:.4f}")
print(f"\nTest Metrics:")
print(f"  AUROC: {test_auc:.4f}")
print(f"  PR-AUC: {pr_auc:.4f}")
print(f"  F1-Score: {test_f1:.4f}")
print(f"  Sensitivity: {sensitivity:.4f}")
print(f"  Specificity: {specificity:.4f}")
print(f"\nClassification Report:")
print(classification_report(y_test, y_test_pred))

os.makedirs("model_output", exist_ok=True)
joblib.dump(model, "model_output/random_forest.pkl")

metrics = {
    "model": "random_forest",
    "optimal_threshold": float(best_threshold),
    "val_auroc": float(val_auc),
    "test_auroc": float(test_auc),
    "test_pr_auc": float(pr_auc),
    "test_f1": float(test_f1),
    "test_sensitivity": float(sensitivity),
    "test_specificity": float(specificity),
    "feature_names": feature_names,
    "feature_importance": model.feature_importances_.tolist()
}

with open("model_output/random_forest_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print("\nModel and metrics saved to model_output/")

