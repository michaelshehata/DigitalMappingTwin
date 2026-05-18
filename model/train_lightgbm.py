import numpy as np
import joblib
import json
import os

import lightgbm as lgb

import sys
sys.path.append(os.path.abspath(".."))

from scripts.load_data import load_all_data

np.random.seed(6001)


# FINAL DEPLOYMENT MODEL CONFIG
model_name = "final_lgbm"

output_dir = "model_output/deployment"

os.makedirs(output_dir, exist_ok=True)


# LOAD DATA
print("Loading full dataset...")

X, y, _ = load_all_data()

X_flat = X.reshape(-1, X.shape[-1])
y_flat = y.flatten()

# Remove invalid pixels
mask = (y_flat >= 0)

X_flat = X_flat[mask]
y_flat = y_flat[mask]

feature_names = [
    "NDVI",
    "Population",
    "Temperature",
    "Elevation",
    "Distance_to_Water",
    "Landcover"
]

print(f"\nDataset Shape: {X_flat.shape}")


# CLASS DISTRIBUTION
unique, counts = np.unique(y_flat, return_counts=True)

print("\nClass Distribution:")

for u, c in zip(unique, counts):
    print(f"  Class {u}: {c}")


# FINAL MODEL
print("\nInitializing LightGBM...")

model = lgb.LGBMClassifier(
    n_estimators=400,
    num_leaves=63,
    learning_rate=0.03,
    scale_pos_weight=12,
    subsample=0.8,
    colsample_bytree=0.8,
    n_jobs=-1,
    random_state=6001
)


# TRAIN FULL MODEL

print(f"Training pixels: {len(X_flat):,}")

model.fit(X_flat, y_flat)

print("\nTraining complete")

# SAVE MODEL
model_path = os.path.join(output_dir, f"{model_name}.pkl")

joblib.dump(model, model_path)

print(f"\nModel saved:")
print(model_path)


# SAVE METADATA
metadata = {

    "model_name": model_name,

    "model_type": "LightGBM",

    "features": feature_names,

    # Best threshold from evaluation experiments
    "optimal_threshold": 0.35,

    "hyperparameters": {

        "n_estimators": 400,
        "num_leaves": 63,
        "learning_rate": 0.03,
        "scale_pos_weight": 12,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": 6001
    },

    "feature_importance": model.feature_importances_.tolist()
}

metadata_path = os.path.join(
    output_dir,
    f"{model_name}_metadata.json"
)

with open(metadata_path, "w") as f:
    json.dump(metadata, f, indent=2)

print("\nMetadata saved:")
print(metadata_path)

print("\nFINAL DEPLOYMENT MODEL READY")