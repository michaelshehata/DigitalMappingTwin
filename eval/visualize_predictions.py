import numpy as np
import matplotlib.pyplot as plt
import rasterio
import joblib
import json
import sys
import os

sys.path.insert(0, "..")

from scripts.load_data import load_all_data

models_to_eval = ["random_forest", "xgboost", "lightgbm"]

X, y, _ = load_all_data()

X_flat = X.reshape(-1, X.shape[-1])

os.makedirs("outputs/eval", exist_ok=True)

print("="*70)
print("SPATIAL PREDICTION VISUALIZATION")
print("="*70)

fig, axes = plt.subplots(2, 3, figsize=(15, 10))

for idx, model_name in enumerate(models_to_eval):
    try:
        model = joblib.load(f"model_output/{model_name}.pkl")

        # Load metrics to get optimal threshold
        with open(f"model_output/{model_name}_metrics.json", "r") as f:
            metrics = json.load(f)
        optimal_threshold = metrics.get("optimal_threshold", 0.3)

        print(f"\nGenerating prediction map for {model_name.upper()}...")

        chunk_size = 100000
        preds = []
        probs = []

        for i in range(0, len(X_flat), chunk_size):
            chunk = X_flat[i:i + chunk_size]
            prob = model.predict_proba(chunk)[:, 1]
            probs.append(prob)
            pred = (prob > optimal_threshold).astype(int)
            preds.append(pred)

        preds = np.concatenate(preds)
        probs = np.concatenate(probs)

        pred_map = preds.reshape(y.shape)
        prob_map = probs.reshape(y.shape)

        # Plot actual on first row
        if idx == 0:
            ax_actual = axes[0, 0]
            im = ax_actual.imshow(y, cmap="RdYlBu_r", vmin=0, vmax=1)
            ax_actual.set_title("Actual Change Map", fontweight='bold')
            ax_actual.axis('off')
            plt.colorbar(im, ax=ax_actual)

        # Plot predictions on first row (idx+1 because idx=0 has actual)
        ax_pred = axes[0, idx + 1] if idx == 0 else axes[0, idx]

        # Plot probability maps on second row
        ax_prob = axes[1, idx]

        im_pred = ax_pred.imshow(pred_map, cmap="RdYlBu_r", vmin=0, vmax=1)
        ax_pred.set_title(f"{model_name.upper()}\nPredictions (threshold={optimal_threshold:.2f})", fontweight='bold')
        ax_pred.axis('off')
        plt.colorbar(im_pred, ax=ax_pred)

        im_prob = ax_prob.imshow(prob_map, cmap="viridis", vmin=0, vmax=1)
        ax_prob.set_title(f"{model_name.upper()}\nProbability Map", fontweight='bold')
        ax_prob.axis('off')
        plt.colorbar(im_prob, ax=ax_prob)

        change_pct = 100 * np.sum(pred_map) / pred_map.size
        print(f"  Change pixels: {np.sum(pred_map):,} / {pred_map.size:,} ({change_pct:.2f}%)")

    except FileNotFoundError:
        print(f"\nGenerating prediction map for {model_name.upper()}: Model file not found (placeholder)")
        ax_pred = axes[0, idx + 1] if idx == 0 else axes[0, idx]
        ax_prob = axes[1, idx]

        ax_pred.text(0.5, 0.5, f"{model_name}\n(Not trained yet)",
                    ha='center', va='center', transform=ax_pred.transAxes)
        ax_prob.text(0.5, 0.5, f"{model_name}\n(Not trained yet)",
                    ha='center', va='center', transform=ax_prob.transAxes)
        ax_pred.axis('off')
        ax_prob.axis('off')

# Remove the extra subplot if it exists
try:
    fig.delaxes(axes[0, 3])
except:
    pass

plt.suptitle("Spatial Prediction and Probability Maps", fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig("outputs/eval/prediction_maps.png", dpi=150, bbox_inches='tight')
print("\n\nPrediction maps saved to: outputs/eval/prediction_maps.png")
