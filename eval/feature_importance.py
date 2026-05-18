import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

results = pd.read_csv("model_output/experiment_results.csv")

top_models = results.sort_values(
    "F1",
    ascending=False
).head(3)

os.makedirs("eval_outputs/plots", exist_ok=True)

print("FEATURE IMPORTANCE ANALYSIS")

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for idx, (_, row) in enumerate(top_models.iterrows()):

    experiment_name = row["Experiment"]
    model_type = row["Model"]

    metrics_path = (
        f"model_output/hyperparameter_tuning/"
        f"{model_type}/"
        f"{experiment_name}_metrics.json"
    )

    print(f"\nLoading: {experiment_name}")

    with open(metrics_path, "r") as f:
        metrics = json.load(f)

    features = np.array(metrics["feature_names"])
    importance = np.array(metrics["feature_importance"])

    importance = importance / np.sum(importance)

    sorted_idx = np.argsort(importance)

    ax = axes[idx]

    ax.barh(
        range(len(sorted_idx)),
        importance[sorted_idx]
    )

    ax.set_yticks(range(len(sorted_idx)))

    ax.set_yticklabels(features[sorted_idx])

    ax.set_xlim(0, 0.35)

    ax.set_xlabel("Normalized Importance")

    ax.set_title(
        f"{experiment_name}\nFeature Importance",
        fontweight="bold"
    )

    ax.grid(axis="x", alpha=0.3)

plt.suptitle(
    "Top 3 Model Feature Importance Comparison",
    fontsize=18,
    fontweight="bold"
)

plt.tight_layout()

plt.savefig(
    "eval_outputs/plots/feature_importance_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

print(
    "\nSaved to "
    "eval_outputs/plots/feature_importance_comparison.png"
)