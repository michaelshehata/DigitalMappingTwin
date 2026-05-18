import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

os.makedirs("eval_outputs/plots", exist_ok=True)
os.makedirs("eval_outputs/reports", exist_ok=True)


# LOAD RESULTS
results = pd.read_csv("model_output/experiment_results.csv")


print("HYPERPARAMETER TUNING RESULTS")


print(results.sort_values("F1", ascending=False).to_string(index=False))


# BEST MODEL
best_model = results.sort_values("F1", ascending=False).iloc[0]

print("\nBEST MODEL")
print(best_model)

best_model.to_frame().T.to_csv(
    "eval_outputs/reports/best_model.csv",
    index=False
)

# BAR CHARTS
metrics = ["F1", "Precision", "Recall", "PR-AUC", "AUROC", "Specificity"]

for metric in metrics:
    plt.figure(figsize=(10, 5))

    sorted_df = results.sort_values(metric, ascending=False)

    sns.barplot(
        data=sorted_df,
        x="Experiment",
        y=metric,
        hue="Model"
    )

    plt.title(f"Model Comparison — {metric}")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(f"eval_outputs/plots/{metric.lower()}_comparison.png", dpi=300)
    plt.close()


# HEATMAP
heatmap_df = results[[
    "Experiment",
    "F1",
    "Precision",
    "Recall",
    "PR-AUC",
    "AUROC",
    "Specificity"
]].set_index("Experiment")

plt.figure(figsize=(10, 6))

sns.heatmap(
    heatmap_df,
    annot=True,
    cmap="viridis",
    fmt=".3f"
)

plt.title("Experiment Performance Heatmap")
plt.tight_layout()

plt.savefig(
    "eval_outputs/plots/performance_heatmap.png",
    dpi=300
)

plt.close()


# SAVE SORTED RESULTS
results.sort_values("F1", ascending=False).to_csv(
    "eval_outputs/reports/full_rankings.csv",
    index=False
)

print("\nEvaluation plots + rankings saved to eval_outputs")