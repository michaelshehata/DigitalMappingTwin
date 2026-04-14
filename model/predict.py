import rasterio
import numpy as np
import joblib
import matplotlib.pyplot as plt

# Load model
model = joblib.load("model/land_model.pkl")

# Load data
with rasterio.open("data/norwich_cover/norwich_2020.tif") as src:
    land2020 = src.read(1)


def predict_map(model, image):
    output = image.copy()

    for i in range(1, image.shape[0] - 1):
        for j in range(1, image.shape[1] - 1):
            patch = image[i-1:i+2, j-1:j+2].flatten().reshape(1, -1)
            pred = model.predict(patch)
            output[i, j] = pred

    return output



# Predict
pred = predict_map(model, land2020)

# Show result
plt.imshow(pred)
plt.title("Predicted Land Use")
plt.colorbar()
plt.show()

with rasterio.open(
    "data/norwich_cover/norwich_2020.tif"
) as src:

    profile = src.profile

with rasterio.open(
    "outputs/predicted_2030.tif",
    "w",
    **profile
) as dst:
    dst.write(pred.astype(rasterio.uint8), 1)