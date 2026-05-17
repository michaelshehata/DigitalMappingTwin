import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import joblib
import json
import sys
import os

sys.path.insert(0, "..")

from scripts.load_data import load_all_data

models_to_eval = ["random_forest", "xgboost", "lightgbm"]

X, y, _ = load_all_data()

X_flat = X.reshape(-1, X.shape[-1])
y_flat = y.flatten()

os.makedirs("outputs/eval", exist_ok=True)

print("="*70)
print("CONFUSION MATRIX ANALYSIS")
print("="*70)

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

cm_data = {}

for idx, (model_name, ax) in enumerate(zip(models_to_eval, axes)):
    try:
        model = joblib.load(f"model_output/{model_name}.pkl")

        # Load metrics to get optimal threshold
        with open(f"model_output/{model_name}_metrics.json", "r") as f:
            metrics = json.load(f)
        optimal_threshold = metrics.get("optimal_threshold", 0.3)

        chunk_size = 100000
        preds = []
        probs = []

        print(f"\nEvaluating {model_name.upper()} (threshold={optimal_threshold:.2f})...")

        for i in range(0, len(X_flat), chunk_size):
            chunk = X_flat[i:i + chunk_size]
            prob = model.predict_proba(chunk)[:, 1]
            probs.append(prob)
            pred = (prob > optimal_threshold).astype(int)
            preds.append(pred)

        preds = np.concatenate(preds)
        cm = confusion_matrix(y_flat, preds)

        tn, fp, fn, tp = cm.ravel()
        accuracy = (tp + tn) / (tp + tn + fp + fn)
        sensitivity = tp / (tp + fn)
        specificity = tn / (tn + fp)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0

        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  Sensitivity (TP Rate): {sensitivity:.4f}")
        print(f"  Specificity (TN Rate): {specificity:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Confusion Matrix:")
        print(f"    TN={tn}, FP={fp}")
        print(f"    FN={fn}, TP={tp}")

        cm_data[model_name] = {
            "confusion_matrix": cm.tolist(),
            "accuracy": float(accuracy),
            "sensitivity": float(sensitivity),
            "specificity": float(specificity),
            "precision": float(precision),
            "threshold": float(optimal_threshold)
        }

        # Plot confusion matrix
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                    xticklabels=['No Change', 'Change'],
                    yticklabels=['No Change', 'Change'],
                    cbar=False)
        ax.set_title(f"{model_name.upper()}\nAccuracy: {accuracy:.4f}")
        ax.set_ylabel("True Label")
        ax.set_xlabel("Predicted Label")

    except FileNotFoundError:
        print(f"\nEvaluating {model_name.upper()}: Model file not found (placeholder)")
        cm_data[model_name] = {
            "confusion_matrix": [[0, 0], [0, 0]],
            "accuracy": 0.0,
            "sensitivity": 0.0,
            "specificity": 0.0,
            "precision": 0.0,
            "threshold": 0.3
        }
        ax.text(0.5, 0.5, f"{model_name}\n(Model not trained yet)",
                ha='center', va='center', transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])

plt.tight_layout()
plt.savefig("outputs/eval/confusion_matrices.png", dpi=150, bbox_inches='tight')
print("\n\nConfusion matrices saved to: outputs/eval/confusion_matrices.png")

with open("outputs/eval/confusion_matrix_summary.json", "w") as f:
    json.dump(cm_data, f, indent=2)
print("Summary saved to: outputs/eval/confusion_matrix_summary.json")
