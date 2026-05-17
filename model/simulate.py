import numpy as np
import rasterio
import joblib
import json
import sys

from scripts.load_data import load_all_data


if len(sys.argv) > 1:
    model_name = sys.argv[1]
else:
    model_name = "xgboost"
    print(f"No model specified. Using default: {model_name}")

print(f"Loading model: {model_name}")
model = joblib.load(f"model_output/{model_name}.pkl")

# Load optimal threshold from metrics
try:
    with open(f"model_output/{model_name}_metrics.json", "r") as f:
        metrics = json.load(f)
    optimal_threshold = metrics.get("optimal_threshold", 0.3)
except:
    optimal_threshold = 0.3
    print(f"Warning: Could not load optimal threshold, using default: {optimal_threshold}")

print(f"Using optimal threshold: {optimal_threshold:.2f}")

X, y, profile = load_all_data()


def simulate(model, X, steps=10, threshold=0.3):
    X_current = X.copy()

    for step in range(steps):
        print(f"  Step {step+1}/{steps}")
        X_flat = X_current.reshape(-1, X.shape[-1])
        prob = model.predict_proba(X_flat)[:, 1]
        pred = (prob > threshold).astype(np.uint8)
        pred_map = pred.reshape(X.shape[:2])
        X_current[..., 0] = X_current[..., 0] * (1 - pred_map)

    return pred_map


print(f"Running forward simulation with {model_name}...")
future = simulate(model, X, steps=10, threshold=optimal_threshold)

print(f"\nSimulation complete")
print(f"Predicted change pixels: {np.sum(future)} / {future.size} ({100*np.sum(future)/future.size:.2f}%)")

with rasterio.open(f"outputs/future_2100_{model_name}.tif", "w", **profile) as dst:
    dst.write(future.astype(np.uint8), 1)

print(f"Saved to: outputs/future_2100_{model_name}.tif")


