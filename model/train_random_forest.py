import os
import joblib
import numpy as np
import rasterio

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(
    BASE_DIR,
    "processed_data"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

os.makedirs(MODEL_DIR, exist_ok=True)


FEATURE_FILES = [
    "elevation.tif",
    "distance_to_water.tif",
    "temperature_2024.tif",
    "population_2020.tif",
    "ndvi_2024.tif",
    "rgb_2024.tif"
]

TARGET_FILE = "landcover_2024.tif"


def load_raster(filepath):

    with rasterio.open(filepath) as src:

        data = src.read()

    return data


def prepare_features():

    feature_arrays = []

    for filename in FEATURE_FILES:

        filepath = os.path.join(
            DATA_DIR,
            filename
        )

        data = load_raster(filepath)

        if data.ndim == 2:
            data = np.expand_dims(data, axis=0)

        feature_arrays.append(data)

    stacked = np.vstack(feature_arrays)

    bands, height, width = stacked.shape

    X = stacked.reshape(
        bands,
        height * width
    ).T

    return X, height, width


def prepare_labels():

    filepath = os.path.join(
        DATA_DIR,
        TARGET_FILE
    )

    with rasterio.open(filepath) as src:

        y = src.read(1)

    y = y.flatten()

    return y


print("\nLoading feature stack...")

X, height, width = prepare_features()

print("Loading labels...")

y = prepare_labels()

print(f"\nFeature matrix shape: {X.shape}")
print(f"Label shape: {y.shape}")

valid_mask = ~np.isnan(X).any(axis=1)

X = X[valid_mask]
y = y[valid_mask]

print(f"\nValid samples: {len(y)}")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


hyperparameter_sets = [

    {
        "name": "rf_iteration_1",
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_split": 2
    },

    {
        "name": "rf_iteration_2",
        "n_estimators": 200,
        "max_depth": 15,
        "min_samples_split": 4
    },

    {
        "name": "rf_iteration_3",
        "n_estimators": 300,
        "max_depth": 20,
        "min_samples_split": 5
    },

    {
        "name": "rf_iteration_4",
        "n_estimators": 500,
        "max_depth": None,
        "min_samples_split": 2
    }
]


results = []


for params in hyperparameter_sets:

    print("\n===================================")
    print(f"Training: {params['name']}")
    print("===================================")

    model = RandomForestClassifier(
        n_estimators=params["n_estimators"],
        max_depth=params["max_depth"],
        min_samples_split=params["min_samples_split"],
        random_state=42,
        n_jobs=-1
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    f1 = f1_score(
        y_test,
        predictions,
        average="weighted"
    )

    print(f"\nAccuracy: {accuracy:.4f}")
    print(f"F1 Score: {f1:.4f}")

    print("\nClassification Report:")
    print(classification_report(
        y_test,
        predictions
    ))

    print("\nConfusion Matrix:")
    print(confusion_matrix(
        y_test,
        predictions
    ))

    model_path = os.path.join(
        MODEL_DIR,
        f"{params['name']}.pkl"
    )

    joblib.dump(
        model,
        model_path
    )

    print(f"\nSaved model to:")
    print(model_path)

    results.append({
        "model": params["name"],
        "accuracy": accuracy,
        "f1_score": f1
    })



print("FINAL RESULTS")


for result in results:

    print(
        f"{result['model']} | "
        f"Accuracy: {result['accuracy']:.4f} | "
        f"F1: {result['f1_score']:.4f}"
    )