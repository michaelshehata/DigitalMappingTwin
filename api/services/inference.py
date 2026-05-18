import numpy as np
import joblib
import json
import os

from scripts.load_data import load_all_data
from api.services.geojson import raster_to_geojson

MODEL_PATH = (
    "model_output/deployment/final_lgbm.pkl"
)

METADATA_PATH = (
    "model_output/deployment/"
    "final_lgbm_metadata.json"
)

model = joblib.load(MODEL_PATH)

with open(METADATA_PATH) as f:
    metadata = json.load(f)

DEFAULT_THRESHOLD = metadata[
    "optimal_threshold"
]

def run_prediction(
    threshold=DEFAULT_THRESHOLD,
    steps=10
):

    X, y, profile = load_all_data()

    height = profile["height"]
    width = profile["width"]

    X_flat = X.reshape(
        -1,
        height,
        width,
        X.shape[-1]
    )

    X_flat = X_flat[0]

    X_flat = X_flat.reshape(
        -1,
        X.shape[-1]
    )

    probabilities = (
        model.predict_proba(X_flat)[:, 1]
    )

    binary = (
        probabilities > threshold
    ).astype(np.uint8)

    probability_map = probabilities.reshape(
        height,
        width
    )

    binary_map = binary.reshape(
        height,
        width
    )

    geojson = raster_to_geojson(
        binary_map
    )

    os.makedirs(
        "api/output",
        exist_ok=True
    )

    geojson_path = (
        "api/output/predictions.geojson"
    )

    with open(geojson_path, "w") as f:
        json.dump(geojson, f)

    return {

        "threshold": threshold,

        "forecast_steps": steps,

        "predicted_change_pixels": int(
            binary.sum()
        ),

        "total_pixels": int(
            binary.size
        ),

        "predicted_change_percentage":
            round(
                100 * binary.mean(),
                2
            ),

        "probability_mean":
            float(probability_map.mean()),

        "probability_std":
            float(probability_map.std()),

        "geojson_file":
            geojson_path
    }