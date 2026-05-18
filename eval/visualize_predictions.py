import numpy as np
import matplotlib.pyplot as plt
import joblib
import pandas as pd
import sys
import os

sys.path.insert(0, "..")

from scripts.load_data import load_all_data

results = pd.read_csv("model_output/experiment_results.csv")

best_model = results.sort_values(
    "F1",
    ascending=False
).iloc[0]

experiment_name = best_model["Experiment"]
model_type = best_model["Model"]
threshold = best_model["Threshold"]

print("=" * 80)
print("BEST MODEL SPATIAL VISUALISATION")
print("=" * 80)

print(f"Experiment: {experiment_name}")
print(f"Model Type: {model_type}")

model_path = (
    f"model_output/hyperparameter_tuning/"
    f"{model_type}/"
    f"{experiment_name}.pkl"
)

model = joblib.load(model_path)

X, y, _ = load_all_data()

X_flat = X.reshape(-1, X.shape[-1])

chunk_size = 100000

preds = []
probs = []

print("\nGenerating predictions...")

for i in range(0, len(X_flat), chunk_size):

    chunk = X_flat[i:i + chunk_size]

    prob = model.predict_proba(chunk)[:, 1]

    pred = (prob > threshold).astype(int)

    preds.append(pred)
    probs.append(prob)

preds = np.concatenate(preds)
probs = np.concatenate(probs)

pred_map = preds.reshape(y.shape)
prob_map = probs.reshape(y.shape)

change_pct = 100 * np.sum(pred_map) / pred_map.size

print(f"Predicted Change Pixels: {change_pct:.2f}%")

os.makedirs("eval_outputs/maps", exist_ok=True)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

im1 = axes[0].imshow(
    y[-1],
    cmap="RdYlBu_r",
    vmin=0,
    vmax=1
)

axes[0].set_title(
    "Actual Change",
    fontweight="bold"
)

axes[0].axis("off")

plt.colorbar(im1, ax=axes[0])

im2 = axes[1].imshow(
    pred_map[-1],
    cmap="RdYlBu_r",
    vmin=0,
    vmax=1
)

axes[1].set_title(
    f"Predicted Change\n{change_pct:.2f}% Pixels",
    fontweight="bold"
)

axes[1].axis("off")

plt.colorbar(im2, ax=axes[1])

im3 = axes[2].imshow(
    prob_map[-1],
    cmap="viridis",
    vmin=0,
    vmax=1
)

axes[2].set_title(
    "Prediction Probability",
    fontweight="bold"
)

axes[2].axis("off")

plt.colorbar(im3, ax=axes[2])

plt.suptitle(
    f"Spatial Prediction Results — {experiment_name}",
    fontsize=18,
    fontweight="bold"
)

plt.tight_layout()

plt.savefig(
    "eval_outputs/maps/best_model_predictions.png",
    dpi=300,
    bbox_inches="tight"
)

print(
    "\nSaved to "
    "eval_outputs/maps/best_model_predictions.png"
)