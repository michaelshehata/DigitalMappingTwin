import numpy as np
import rasterio
import joblib

from scripts.load_data import load_all_data
from api.weather_api import get_live_weather
from api.rasterize_live import inject_live_data


# Load model
model = joblib.load("model_output/land_model.pkl")

# Load data
X, y, profile = load_all_data()

# Flatten
X_flat = X.reshape(-1, X.shape[-1])

# Predict
y_pred = model.predict(X_flat)

# Reshape
pred_map = y_pred.reshape(y.shape)

print("Prediction done")

# Save
with rasterio.open("outputs/predicted_map.tif", "w", **profile) as dst:
    dst.write(pred_map.astype(rasterio.uint8), 1)