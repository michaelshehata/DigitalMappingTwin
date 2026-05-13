import numpy as np
import rasterio
import joblib

from scripts.load_data import load_all_data


model = joblib.load("model_output/random_forest.pkl")

X, y, profile = load_all_data()

X_flat = X.reshape(-1, X.shape[-1])

print("Running prediction in chunks:")

chunk_size = 50000  # adjust if needed
preds = []

for i in range(0, len(X_flat), chunk_size):
    print(f"Processing chunk {i} -> {i + chunk_size}")

    chunk = X_flat[i:i + chunk_size]

    prob = model.predict_proba(chunk)[:, 1]
    pred = (prob > 0.3).astype(np.uint8)

    preds.append(pred)

preds = np.concatenate(preds)

pred_map = preds.reshape(y.shape)

print("Prediction complete")

with rasterio.open("outputs/predicted_map.tif", "w", **profile) as dst:
    dst.write(pred_map, 1)