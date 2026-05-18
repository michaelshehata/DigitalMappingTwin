import numpy as np
import joblib
import json
import sys
import pandas as pd
import os

from sklearn.metrics import (
    classification_report,
    f1_score,
    roc_auc_score,
    precision_recall_curve,
    auc,
    confusion_matrix,
    accuracy_score
)

sys.path.insert(0, "..")

from scripts.load_data import load_all_data


# LOAD EXPERIMENT RESULTS
results = pd.read_csv("experiment_results.csv")

best_row = results.sort_values("F1", ascending=False).iloc[0]

experiment_name = best_row["Experiment"]
model_type = best_row["Model"]
threshold = best_row["Threshold"]


print("BEST MODEL EVALUATION")


print(f"Experiment: {experiment_name}")
print(f"Model Type: {model_type}")
print(f"F1 Score:   {best_row['F1']:.4f}")
print(f"AUROC:      {best_row['AUROC']:.4f}")
print(f"PR-AUC:     {best_row['PR-AUC']:.4f}")
print(f"Threshold:  {threshold:.2f}")


# LOAD MODEL
model_path = f"model_output/hyperparameter_tuning/{model_type}/{experiment_name}.pkl"

model = joblib.load(model_path)


# LOAD DATA
X, y, _ = load_all_data()

X_flat = X.reshape(-1, X.shape[-1])
y_flat = y.flatten()


# PREDICTIONS
chunk_size = 100000

preds = []
probs = []

for i in range(0, len(X_flat), chunk_size):
    chunk = X_flat[i:i + chunk_size]

    prob = model.predict_proba(chunk)[:, 1]
    pred = (prob > threshold).astype(int)

    preds.append(pred)
    probs.append(prob)

preds = np.concatenate(preds)
probs = np.concatenate(probs)


# METRICS
accuracy = accuracy_score(y_flat, preds)
f1 = f1_score(y_flat, preds)
auroc = roc_auc_score(y_flat, probs)

precision, recall, _ = precision_recall_curve(y_flat, probs)
pr_auc = auc(recall, precision)

tn, fp, fn, tp = confusion_matrix(y_flat, preds).ravel()

sensitivity = tp / (tp + fn)
specificity = tn / (tn + fp)

print("\nFINAL EVALUATION")
print(f"Accuracy:    {accuracy:.4f}")
print(f"F1 Score:   {f1:.4f}")
print(f"AUROC:      {auroc:.4f}")
print(f"PR-AUC:     {pr_auc:.4f}")
print(f"Sensitivity:{sensitivity:.4f}")
print(f"Specificity:{specificity:.4f}")

print("\nCONFUSION MATRIX")
print(f"TN: {tn}")
print(f"FP: {fp}")
print(f"FN: {fn}")
print(f"TP: {tp}")

report = classification_report(
    y_flat,
    preds,
    target_names=["No Change", "Change"]
)

print("\nCLASSIFICATION REPORT")
print(report)

os.makedirs("eval_outputs/reports", exist_ok=True)

with open("eval_outputs/reports/final_evaluation.txt", "w") as f:
    f.write(report)

summary = {
    "experiment": experiment_name,
    "model_type": model_type,
    "accuracy": float(accuracy),
    "f1": float(f1),
    "auroc": float(auroc),
    "pr_auc": float(pr_auc),
    "sensitivity": float(sensitivity),
    "specificity": float(specificity),
    "threshold": float(threshold)
}

with open("eval_outputs/reports/final_metrics.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\nEvaluation saved to eval_outputs/reports")