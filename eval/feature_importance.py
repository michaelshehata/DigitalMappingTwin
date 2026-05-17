import json
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

sys.path.insert(0, "..")

models_to_eval = ["random_forest", "xgboost", "lightgbm"]

print("="*70)
print("FEATURE IMPORTANCE ANALYSIS")
print("="*70)

importance_data = {}

for model_name in models_to_eval:
    try:
        with open(f"model_output/{model_name}_metrics.json", "r") as f:
            metrics = json.load(f)

        importance_data[model_name] = {
            "features": metrics["feature_names"],
            "importance": metrics["feature_importance"]
        }
        print(f"\n{model_name.upper()}:")
        for feat, imp in zip(metrics["feature_names"], metrics["feature_importance"]):
            print(f"  {feat}: {imp:.4f}")
    except FileNotFoundError:
        print(f"\n{model_name.upper()}: Metrics file not found (placeholder)")
        importance_data[model_name] = {
            "features": ["NDVI", "Population", "Temperature", "Elevation", "Distance_to_Water"],
            "importance": [0.0] * 5
        }

os.makedirs("outputs/eval", exist_ok=True)

# Create comparison plots
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for idx, (model_name, ax) in enumerate(zip(models_to_eval, axes)):
    features = importance_data[model_name]["features"]
    importance = importance_data[model_name]["importance"]

    sorted_idx = np.argsort(importance)

    ax.barh(range(len(sorted_idx)), np.array(importance)[sorted_idx])
    ax.set_yticks(range(len(sorted_idx)))
    ax.set_yticklabels(np.array(features)[sorted_idx])
    ax.set_xlabel("Importance")
    ax.set_title(f"{model_name.upper()}\nFeature Importance")
    ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig("outputs/eval/feature_importance_comparison.png", dpi=150, bbox_inches='tight')
print("\n\nFeature importance comparison saved to: outputs/eval/feature_importance_comparison.png")

with open("outputs/eval/feature_importance_summary.json", "w") as f:
    json.dump(importance_data, f, indent=2)
print("Summary saved to: outputs/eval/feature_importance_summary.json")
