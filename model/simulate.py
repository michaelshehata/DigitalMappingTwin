import os
import rasterio
import numpy as np
import joblib
import matplotlib.pyplot as plt

model = joblib.load("model/land_model.pkl")

with rasterio.open("data/norwich_cover/norwich_2021.tif") as src:
    current = src.read(1)
    profile = src.profile

os.makedirs("outputs", exist_ok=True)

print("Initial map loaded:", current.shape)


def predict_map_chunked(model, image, batch_size=50000):
    patches = []
    coords = []

    for i in range(1, image.shape[0] - 1):
        for j in range(1, image.shape[1] - 1):
            patch = image[i-1:i+2, j-1:j+2].flatten()
            patches.append(patch)
            coords.append((i, j))

    patches = np.array(patches)
    output = image.copy()

    for start in range(0, len(patches), batch_size):
        end = start + batch_size
        batch = patches[start:end]
        preds = model.predict(batch)

        for (i, j), pred in zip(coords[start:end], preds):
            output[i, j] = pred

        print(f"Processed {min(end, len(patches))} / {len(patches)}")

    return output


steps = 10

for step in range(steps):
    print(f"Starting step {step + 1}")
    current = predict_map_chunked(model, current)
    print(f"Step {step + 1} complete")


plt.imshow(current)
plt.title("Future Land Use Simulation")
plt.colorbar()
plt.show()


profile.update(dtype=rasterio.uint8, count=1)

with rasterio.open("outputs/future_2100.tif", "w", **profile) as dst:
    dst.write(current.astype(rasterio.uint8), 1)

print("Saved to outputs/future_2100.tif")