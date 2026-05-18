import numpy as np
import matplotlib.pyplot as plt
import joblib
import json
import sys
import os
import pandas as pd

sys.path.insert(0, "..")

from scripts.load_data import load_all_data

results = pd.read_csv("model_output/experiment_results.csv")

best_model = results.sort_values(
    "F1",
    ascending=False
).iloc[0]

experiment_name = best_model["Experiment"]
model_type = best_model["Model"]

X, y, _ = load_all_data()

os.makedirs("eval_outputs/plots", exist_ok=True)

print("SCENARIO ANALYSIS")

model = joblib.load(
    f"model_output/hyperparameter_tuning/"
    f"{model_type}/"
    f"{experiment_name}.pkl"
)

with open(
    f"model_output/hyperparameter_tuning/"
    f"{model_type}/"
    f"{experiment_name}_metrics.json",
    "r"
) as f:
    metrics = json.load(f)

optimal_threshold = metrics.get("optimal_threshold", 0.3)

print(
    f"\n{experiment_name} "
    f"Scenarios (threshold={optimal_threshold:.2f})"
)

def run_scenario(X_mod):

    X_flat = X_mod.reshape(-1, X_mod.shape[-1])

    preds = []

    chunk_size = 100000

    for i in range(0, len(X_flat), chunk_size):

        chunk = X_flat[i:i + chunk_size]

        prob = model.predict_proba(chunk)[:, 1]

        pred = (prob > optimal_threshold).astype(int)

        preds.append(pred)

    preds = np.concatenate(preds)

    return preds.reshape(y.shape)

baseline = run_scenario(X)

X_growth = X.copy()
X_growth[..., 1] = np.minimum(X_growth[..., 1] * 1.5, 1.0)
growth = run_scenario(X_growth)

X_conserve = X.copy()
X_conserve[..., 0] = np.minimum(X_conserve[..., 0] * 1.2, 1.0)
conserve = run_scenario(X_conserve)

X_climate = X.copy()
X_climate[..., 2] = np.minimum(X_climate[..., 2] + 0.1, 1.0)
climate = run_scenario(X_climate)

fig, axes = plt.subplots(1, 4, figsize=(20, 5))

scenarios = [
    ("Baseline", baseline),
    ("Urban Growth\n(+50% Population)", growth),
    ("Conservation\n(+20% NDVI)", conserve),
    ("Climate Stress\n(+2°C)", climate)
]

for idx, (title, pred_map) in enumerate(scenarios):

    ax = axes[idx]

    im = ax.imshow(
        pred_map[-1],
        cmap="RdYlBu_r",
        vmin=0,
        vmax=1
    )

    change_pct = (
        100 * np.sum(pred_map) / pred_map.size
    )

    ax.set_title(
        f"{title}\n{change_pct:.2f}% Change",
        fontsize=11,
        fontweight="bold"
    )

    ax.axis("off")

    plt.colorbar(
        im,
        ax=ax,
        fraction=0.046,
        pad=0.04
    )

plt.suptitle(
    f"Scenario Analysis — {experiment_name}",
    fontsize=18,
    fontweight="bold"
)

plt.tight_layout()

plt.savefig(
    "eval_outputs/plots/scenario_analysis.png",
    dpi=300,
    bbox_inches="tight"
)

print(
    "\nScenario analysis saved to "
    "eval_outputs/plots/scenario_analysis.png"
)