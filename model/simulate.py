import numpy as np
import rasterio
import joblib

from scripts.load_data import load_all_data


model = joblib.load("model_output/random_forest.pkl")

X, y, profile = load_all_data()


def simulate(model, X, steps=10):
    X_current = X.copy()

    for step in range(steps):
        print(f"Step {step+1}")

        X_flat = X_current.reshape(-1, X.shape[-1])

        prob = model.predict_proba(X_flat)[:, 1]
        pred = (prob > 0.3).astype(np.uint8)

        pred_map = pred.reshape(X.shape[:2])

        # simple update: inject change into NDVI channel
        X_current[..., 0] = X_current[..., 0] * (1 - pred_map)

    return pred_map


future = simulate(model, X, steps=10)

with rasterio.open("outputs/future_2100.tif", "w", **profile) as dst:
    dst.write(future.astype(np.uint8), 1)

print("Simulation complete")