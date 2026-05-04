import numpy as np
import rasterio
import joblib

from scripts.load_data import load_all_data
from api.weather_api import get_live_weather
from api.rasterize_live import inject_live_data


model = joblib.load("model/land_model.pkl")

X, y, profile = load_all_data()

current = y.copy()  # starting state


def simulate(model, X, steps=10):
    X_flat = X.reshape(-1, X.shape[-1])

    for step in range(steps):
        print(f"Step {step + 1}")

        pred = model.predict(X_flat)
        pred_map = pred.reshape(X.shape[:2])

        # Update only target (not features for now)
        current = pred_map

    return current


future = simulate(model, X, steps=10)


with rasterio.open("outputs/future_2100.tif", "w", **profile) as dst:
    dst.write(future.astype(rasterio.uint8), 1)

print("Simulation complete")