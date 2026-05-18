import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, f1_score, roc_auc_score
import joblib
import pandas as pd
import sys
import os

sys.path.insert(0, "..")

from scripts.load_data import load_all_data

results = pd.read_csv("model_output/experiment_results.csv")

top_models = results.sort_values(
    "F1",
    ascending=False
).head(3)

X, y, _ = load_all_data()

X_flat = X.reshape(-1, X.shape[-1])
y_flat = y.flatten()

os.makedirs("eval_outputs/plots", exist_ok=True)

print("CONFUSION MATRIX ANALYSIS")

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

for idx, (_, row) in enumerate(top_models.iterrows()):

    experiment_name = row["Experiment"]
    model_type = row["Model"]
    threshold = row["Threshold"]

    print(f"\nEvaluating {experiment_name}")

    model_path = (
        f"model_output/hyperparameter_tuning/"
        f"{model_type}/"
        f"{experiment_name}.pkl"
    )

    model = joblib.load(model_path)

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

    cm = confusion_matrix(y_flat, preds)

    f1 = f1_score(y_flat, preds)
    auroc = roc_auc_score(y_flat, probs)

    ax = axes[idx]

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=False,
        xticklabels=["No Change", "Change"],
        yticklabels=["No Change", "Change"],
        ax=ax
    )

    ax.set_title(
        f"{experiment_name}\nF1={f1:.3f} | AUROC={auroc:.3f}",
        fontweight="bold"
    )

    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")

plt.suptitle(
    "Top 3 Model Confusion Matrices",
    fontsize=18,
    fontweight="bold"
)

plt.tight_layout()

plt.savefig(
    "eval_outputs/plots/confusion_matrices.png",
    dpi=300,
    bbox_inches="tight"
)

print("\nSaved to eval_outputs/plots/confusion_matrices.png")