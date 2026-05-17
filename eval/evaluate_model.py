import numpy as np
import joblib
import json
import sys
import pandas as pd

sys.path.insert(0, "..")

from scripts.load_data import load_all_data
from sklearn.metrics import (
    classification_report, f1_score, roc_auc_score,
    precision_recall_curve, auc, confusion_matrix, accuracy_score
)


models_to_eval = ["random_forest", "xgboost", "lightgbm"]

X, y, _ = load_all_data()

X_flat = X.reshape(-1, X.shape[-1])
y_flat = y.flatten()

chunk_size = 100000
results_summary = []

print("="*80)
print("MODEL EVALUATION ON FULL DATASET")
print("="*80)

for model_name in models_to_eval:
    print(f"\n\nEvaluating: {model_name.upper()}")
    print("-" * 80)

    try:
        model = joblib.load(f"model_output/{model_name}.pkl")

        # Load metrics to get optimal threshold
        with open(f"model_output/{model_name}_metrics.json", "r") as f:
            train_metrics = json.load(f)
        optimal_threshold = train_metrics.get("optimal_threshold", 0.3)

    except FileNotFoundError:
        print(f"  ERROR: Model file not found at model_output/{model_name}.pkl")
        print(f"  Please run: python -m model.train_{model_name}")
        continue

    print(f"  Using optimal threshold: {optimal_threshold:.2f}")
    print("  Processing in chunks...")

    preds = []
    probs = []

    for i in range(0, len(X_flat), chunk_size):
        chunk = X_flat[i:i + chunk_size]
        prob = model.predict_proba(chunk)[:, 1]
        pred = (prob > optimal_threshold).astype(int)
        preds.append(pred)
        probs.append(prob)

    preds = np.concatenate(preds)
    probs = np.concatenate(probs)

    accuracy = accuracy_score(y_flat, preds)
    f1 = f1_score(y_flat, preds)
    auroc = roc_auc_score(y_flat, probs)

    precision, recall, _ = precision_recall_curve(y_flat, probs)
    pr_auc = auc(recall, precision)

    tn, fp, fn, tp = confusion_matrix(y_flat, preds).ravel()
    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    precision_pos = tp / (tp + fp) if (tp + fp) > 0 else 0

    print(f"\n  FULL DATASET METRICS:")
    print(f"    Accuracy:    {accuracy:.4f}")
    print(f"    F1-Score:    {f1:.4f}")
    print(f"    AUROC:       {auroc:.4f}")
    print(f"    PR-AUC:      {pr_auc:.4f}")
    print(f"    Sensitivity: {sensitivity:.4f}")
    print(f"    Specificity: {specificity:.4f}")
    print(f"    Precision:   {precision_pos:.4f}")

    print(f"\n  CONFUSION MATRIX:")
    print(f"    True Negatives:  {tn:,}")
    print(f"    False Positives: {fp:,}")
    print(f"    False Negatives: {fn:,}")
    print(f"    True Positives:  {tp:,}")

    print(f"\n  CLASSIFICATION REPORT:")
    print(classification_report(y_flat, preds, target_names=["No Change", "Change"]))

    results_summary.append({
        "Model": model_name,
        "Threshold": optimal_threshold,
        "Accuracy": accuracy,
        "Precision": precision_pos,
        "F1": f1,
        "AUROC": auroc,
        "PR-AUC": pr_auc,
        "Sensitivity": sensitivity,
        "Specificity": specificity
    })

print("\n\n" + "="*80)
print("COMPARISON SUMMARY")
print("="*80)

if results_summary:
    df = pd.DataFrame(results_summary)
    print("\n" + df.to_string(index=False))

    print("\n\nRanking by key metrics:")
    print("-" * 80)
    for metric in ["F1", "AUROC", "PR-AUC", "Sensitivity", "Specificity"]:
        if metric in df.columns:
            print(f"\n{metric} Ranking:")
            ranked = df.sort_values(metric, ascending=False)
            for i, row in ranked.iterrows():
                print(f"  {i+1}. {row['Model']:15s} (Threshold={row['Threshold']:.2f}): {row[metric]:.4f}")

    with open("model_output/evaluation_summary.json", "w") as f:
        json.dump(results_summary, f, indent=2)

    print("\n\nEvaluation summary saved to: model_output/evaluation_summary.json")
else:
    print("\nNo models evaluated. Please train models first.")

