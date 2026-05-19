import numpy as np
import joblib
import json
import os

from live.load_live_data import load_live_data

from api.services.geojson import (
    raster_to_geojson
)

MODEL_PATH = (
    "model_output/deployment/final_lgbm.pkl"
)

METADATA_PATH = (
    "model_output/deployment/"
    "final_lgbm_metadata.json"
)



# LOAD MODEL
model = joblib.load(MODEL_PATH)

with open(METADATA_PATH) as f:
    metadata = json.load(f)

DEFAULT_THRESHOLD = metadata[
    "optimal_threshold"
]



# MAIN PREDICTION FUNCTION
def run_prediction(

    threshold=DEFAULT_THRESHOLD,

    steps=10

):

    print("\nRUNNING LIVE INFERENCE")
    print("=" * 50)



    # LOAD LIVE FEATURE STACK
    X_live, profile = load_live_data()

    height = profile["height"]

    width = profile["width"]


    # FLATTEN FEATURES
    X_flat = X_live.reshape(
        -1,
        X_live.shape[-1]
    )



    # MODEL INFERENCE
    probabilities = (
        model.predict_proba(X_flat)[:, 1]
    )

    binary = (
        probabilities > threshold
    ).astype(np.uint8)



    # RESHAPE OUTPUTS
    probability_map = probabilities.reshape(
        height,
        width
    )

    binary_map = binary.reshape(
        height,
        width
    )


    os.makedirs(
        "api/output",
        exist_ok=True
    )



    # SAVE PROBABILITY RASTER


    probability_path = (
        "api/output/live_probability.npy"
    )

    np.save(
        probability_path,
        probability_map
    )



    # GENERATE GEOJSON


    geojson = raster_to_geojson(
        binary_map
    )

    geojson_path = (
        "api/output/predictions.geojson"
    )

    with open(geojson_path, "w") as f:

        json.dump(
            geojson,
            f
        )



    # SUMMARY METRICS


    predicted_pixels = int(
        binary.sum()
    )

    total_pixels = int(
        binary.size
    )

    percentage = round(
        100 * binary.mean(),
        2
    )

    probability_mean = float(
        probability_map.mean()
    )

    probability_std = float(
        probability_map.std()
    )


    print("\nLIVE INFERENCE COMPLETE")
    print("=" * 50)

    print(
        f"Predicted change: "
        f"{percentage}%"
    )

    print(
        f"Probability mean: "
        f"{probability_mean:.4f}"
    )

    print(
        f"GeoJSON saved: "
        f"{geojson_path}"
    )



    # API RESPONSE


    return {

        "mode": "live_hybrid_inference",

        "threshold": threshold,

        "forecast_steps": steps,

        "predicted_change_pixels":
            predicted_pixels,

        "total_pixels":
            total_pixels,

        "predicted_change_percentage":
            percentage,

        "probability_mean":
            probability_mean,

        "probability_std":
            probability_std,

        "geojson_file":
            geojson_path,

        "temperature_live": True,

        "ndvi_live": True,

        "static_features": [

            "population",
            "elevation",
            "water",
            "landcover"
        ]
    }