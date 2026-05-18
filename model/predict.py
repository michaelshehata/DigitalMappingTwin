import numpy as np
import rasterio
import joblib
import json
import os
import sys

from scripts.load_data import load_all_data


if len(sys.argv) > 1:
    model_name = sys.argv[1]
else:
    model_name = "final_lgbm"


model_dir = "model_output/deployment"

model_path = os.path.join(
    model_dir,
    f"{model_name}.pkl"
)

metadata_path = os.path.join(
    model_dir,
    f"{model_name}_metadata.json"
)


print(f"\nLoading model: {model_name}")

model = joblib.load(model_path)


with open(metadata_path, "r") as f:
    metadata = json.load(f)

optimal_threshold = metadata.get("optimal_threshold", 0.35)

print(f"Using threshold: {optimal_threshold}")


print("\nLoading environmental data...")

X, y, profile = load_all_data()

print("X shape:", X.shape)
print("y shape:", y.shape)

height = profile["height"]
width = profile["width"]

X_flat = X.reshape(-1, height, width, X.shape[-1])

X_flat = X_flat[0]

X_flat = X_flat.reshape(-1, X.shape[-1])

print(f"Total Pixels: {len(X_flat)}")


chunk_size = 50000

binary_preds = []
probability_preds = []

print("\nRunning prediction in chunks...")

for i in range(0, len(X_flat), chunk_size):

    chunk = X_flat[i:i + chunk_size]

    probs = model.predict_proba(chunk)[:, 1]

    preds = (probs > optimal_threshold).astype(np.uint8)

    probability_preds.append(probs)
    binary_preds.append(preds)

    print(f"Processed {min(i + chunk_size, len(X_flat))} / {len(X_flat)} pixels")


probability_preds = np.concatenate(probability_preds)
binary_preds = np.concatenate(binary_preds)

probability_map = probability_preds.reshape(height, width)
binary_map = binary_preds.reshape(height, width)


output_dir = "outputs"

os.makedirs(output_dir, exist_ok=True)


probability_profile = profile.copy()

probability_profile.update(
    dtype=rasterio.float32,
    count=1
)

probability_output = os.path.join(
    output_dir,
    f"probability_map_{model_name}.tif"
)

with rasterio.open(
    probability_output,
    "w",
    **probability_profile
) as dst:

    dst.write(probability_map.astype(np.float32), 1)

print(f"\nProbability map saved:")
print(probability_output)


binary_profile = profile.copy()

binary_profile.update(
    dtype=rasterio.uint8,
    count=1
)

binary_output = os.path.join(
    output_dir,
    f"binary_prediction_{model_name}.tif"
)

with rasterio.open(
    binary_output,
    "w",
    **binary_profile
) as dst:

    dst.write(binary_map.astype(np.uint8), 1)

print(f"\nBinary prediction map saved:")
print(binary_output)


change_pixels = np.sum(binary_map)

total_pixels = binary_map.size

print("\nPrediction Complete")

print(
    f"Predicted change pixels: "
    f"{change_pixels} / {total_pixels} "
    f"({100 * change_pixels / total_pixels:.2f}%)"
)

print("\nProbability Statistics")

print("Min:", probability_map.min())
print("Max:", probability_map.max())
print("Mean:", probability_map.mean())
print("Std:", probability_map.std())
