import rasterio
import numpy as np
import joblib
from sklearn.metrics import accuracy_score

# Load model
model = joblib.load("model/land_model.pkl")

# Load data
with rasterio.open("data/norwich_cover/norwich_2020.tif") as src:
    land2020 = src.read(1)

with rasterio.open("data/norwich_cover/norwich_2021.tif") as src:
    land2021 = src.read(1)


def predict_map(model, image):
    output = image.copy()

    for i in range(1, image.shape[0] - 1):
        for j in range(1, image.shape[1] - 1):
            patch = image[i-1:i+2, j-1:j+2].flatten().reshape(1, -1)
            pred = model.predict(patch)
            output[i, j] = pred

    return output


print("Predicting 2021 from 2020...")
pred_2021 = predict_map(model, land2020)

# Flatten for comparison
mask = (land2021 > 0)

y_true = land2021[mask]
y_pred = pred_2021[mask]

print("Validation Accuracy:", accuracy_score(y_true, y_pred))