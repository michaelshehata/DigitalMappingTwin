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
X_flat = X.reshape(-1, X.shape[-1])

print("Running prediction in chunks:")

chunk_size = 50000
preds = []

for i in range(0, len(X_flat), chunk_size):
    chunk = X_flat[i:i + chunk_size]
    prob = model.predict_proba(chunk)[:, 1]
    pred = (prob > optimal_threshold).astype(np.uint8)
    preds.append(pred)
    print(f"  Processed {i + chunk_size} / {len(X_flat)} pixels")

preds = np.concatenate(preds)
pred_map = preds.reshape(y.shape)

print("\nPrediction complete")
print(f"Change pixels: {np.sum(pred_map)} / {pred_map.size} ({100*np.sum(pred_map)/pred_map.size:.2f}%)")

with rasterio.open(f"outputs/predicted_map_{model_name}.tif", "w", **profile) as dst:
    dst.write(pred_map, 1)

print(f"Saved to: outputs/predicted_map_{model_name}.tif")


