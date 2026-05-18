import numpy as np
import rasterio
import joblib
import json
import os
import sys

from scripts.load_data import load_all_data


# MODEL NAME
if len(sys.argv) > 1:
    model_name = sys.argv[1]
else:
    model_name = "final_lgbm"


# PATHS
model_dir = "model_output/deployment"

model_path = os.path.join(
    model_dir,
    f"{model_name}.pkl"
)

metadata_path = os.path.join(
    model_dir,
    f"{model_name}_metadata.json"
)


# LOAD MODEL
print(f"\nLoading model: {model_name}")

model = joblib.load(model_path)


# LOAD METADATA
with open(metadata_path, "r") as f:
    metadata = json.load(f)

optimal_threshold = metadata.get("optimal_threshold", 0.35)

print(f"Using threshold: {optimal_threshold}")


# LOAD DATA
print("\nLoading environmental data...")

X, y, profile = load_all_data()


# SIMULATION FUNCTION
def simulate(model, X, height, width, steps=10, threshold=0.35):

    X_current = X.copy()

    for step in range(steps):

        print(f"\nSimulation Step {step + 1}/{steps}")

        X_flat = X_current.reshape(
            -1,
            height,
            width,
            X.shape[-1]
        )

        X_flat = X_flat[0]

        X_flat = X_flat.reshape(-1, X.shape[-1])

        probabilities = model.predict_proba(X_flat)[:, 1]

        predictions = (
            probabilities > threshold
        ).astype(np.uint8)

        prediction_map = predictions.reshape(height, width)

        X_current[0, :, :, 0] = (
            X_current[0, :, :, 0] * (1 - prediction_map)
        )

    return prediction_map


# RUN SIMULATION
print("\nRunning future environmental simulation...")

height = profile["height"]
width = profile["width"]

future_map = simulate(
    model,
    X,
    height,
    width,
    steps=10,
    threshold=optimal_threshold
)


# OUTPUT DIRECTORY
output_dir = "outputs"

os.makedirs(output_dir, exist_ok=True)


# SAVE OUTPUT
output_path = os.path.join(
    output_dir,
    f"future_2100_{model_name}.tif"
)

profile.update(dtype=rasterio.uint8)

with rasterio.open(
    output_path,
    "w",
    **profile
) as dst:

    dst.write(future_map.astype(np.uint8), 1)


# SUMMARY
change_pixels = np.sum(future_map)

total_pixels = future_map.size

print("\nSimulation Complete")

print(
    f"Predicted future change pixels: "
    f"{change_pixels} / {total_pixels} "
    f"({100 * change_pixels / total_pixels:.2f}%)"
)

print(f"\nSaved simulation to:")
print(output_path)