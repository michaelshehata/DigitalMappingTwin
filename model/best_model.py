import os
import time
import warnings

import joblib
import numpy as np
import rasterio

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler

warnings.filterwarnings("ignore")



# CONFIG

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "processed_data")
RESULTS_DIR = os.path.join(BASE_DIR, "model_results")
BEST_MODEL_DIR = os.path.join(BASE_DIR, "best_model")

# Create output directories if missing
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(BEST_MODEL_DIR, exist_ok=True)

SNAPSHOT_YEARS = [1985, 1995, 2005, 2015, 2024]

NODATA_LABEL = 255

# Best Random Forest configuration
RF3_PARAMS = {
    "n_estimators": 300,
    "max_depth": None,
    "min_samples_split": 10,
    "class_weight": "balanced",
    "n_jobs": -1,
    "random_state": 6001,
}

CLASS_NAMES = {
    0: "Vegetation",
    1: "Agricultural",
    2: "Urban",
    3: "Water",
    4: "Sparse",
}



# RASTER LOADER


def load_raster(path: str) -> np.ndarray:
    """
    Load raster as float32 numpy array.

    Returns:
        Array shape:
            (bands, H, W)
    """
    with rasterio.open(path) as src:
        data = src.read()

    return data.astype(np.float32)



# FEATURE STACK BUILDER


def build_feature_stack(year: int):
    """
    Build feature matrix and labels for one snapshot year.

    Returns:
        X_valid : (N, F) float32
        y_valid : (N,) int32
    """

    rgb = load_raster(os.path.join(DATA_DIR, f"rgb_{year}.tif"))
    ndvi = load_raster(os.path.join(DATA_DIR, f"ndvi_{year}.tif"))
    temp = load_raster(os.path.join(DATA_DIR, f"temperature_{year}.tif"))

    elevation = load_raster(os.path.join(DATA_DIR, "elevation.tif"))
    water = load_raster(os.path.join(DATA_DIR, "distance_to_water.tif"))

    labels = load_raster(
        os.path.join(DATA_DIR, f"labels_{year}.tif")
    )[0]

    # Population snapshot selection
    if year <= 2005:
        population = load_raster(
            os.path.join(DATA_DIR, "population_2000.tif")
        )

    elif year <= 2015:
        population = load_raster(
            os.path.join(DATA_DIR, "population_2010.tif")
        )

    else:
        population = load_raster(
            os.path.join(DATA_DIR, "population_2020.tif")
        )

    
    # Feature stacking
    

    feature_list = []

    for i in range(rgb.shape[0]):
        feature_list.append(rgb[i])

    for i in range(ndvi.shape[0]):
        feature_list.append(ndvi[i])

    for i in range(temp.shape[0]):
        feature_list.append(temp[i])

    for i in range(population.shape[0]):
        feature_list.append(population[i])

    feature_list.append(elevation[0])
    feature_list.append(water[0])

    # Shape:
    #   (H, W, F)
    X_full = np.stack(feature_list, axis=-1)

    h, w, f = X_full.shape

    # Flatten
    X_flat = X_full.reshape(-1, f)
    y_flat = labels.reshape(-1)

    # Remove NoData pixels
    valid_mask = (
        (y_flat >= 0) &
        (y_flat != NODATA_LABEL)
    )

    X_valid = X_flat[valid_mask]
    y_valid = y_flat[valid_mask].astype(np.int32)

    return X_valid, y_valid



# CLASS DISTRIBUTION REPORTER


def report_class_distribution(
    y: np.ndarray,
    label: str = "Dataset"
):
    """
    Print dataset class distribution.
    """

    total = len(y)

    print(f"\n{label}")
    print(f"Total valid pixels: {total:,}\n")

    for class_id, class_name in CLASS_NAMES.items():

        count = int(np.sum(y == class_id))

        pct = (
            count / total * 100
            if total > 0 else 0.0
        )

        bar = "█" * int(pct / 2)

        print(
            f"{class_id}  "
            f"{class_name:<15}  "
            f"{count:>10,} px  "
            f"({pct:5.1f}%)  "
            f"{bar}"
        )



# MAIN


def main():


    print("FULL DATASET TRAINING")


    
    # Load all snapshot years
    

    X_parts = []
    y_parts = []

    for year in SNAPSHOT_YEARS:

        print(f"Loading year {year}...")

        X_year, y_year = build_feature_stack(year)

        X_parts.append(X_year)
        y_parts.append(y_year)

        print(
            f"  Valid pixels: {len(y_year):,} | "
            f"Features: {X_year.shape[1]}"
        )

    # Concatenate all years
    X_all = np.concatenate(X_parts, axis=0)
    y_all = np.concatenate(y_parts, axis=0)


    print("FULL DATASET SUMMARY")


    print(f"Total pixels : {len(y_all):,}")
    print(f"Features     : {X_all.shape[1]}")

    report_class_distribution(
        y_all,
        "Full concatenated dataset"
    )

    
    # Scale features


    scaler = MinMaxScaler()

    X_all_scaled = scaler.fit_transform(X_all)

    # Save scaler
    scaler_path = os.path.join(
        BEST_MODEL_DIR,
        "rf3_final_scaler.pkl"
    )

    joblib.dump(scaler, scaler_path)

    print(f"Scaler saved → {scaler_path}")

    
    # Train model
    

    print("\nTraining Random Forest...\n")

    print("Parameters:")
    for k, v in RF3_PARAMS.items():
        print(f"  {k}: {v}")

    model = RandomForestClassifier(**RF3_PARAMS)

    start_time = time.time()

    model.fit(X_all_scaled, y_all)

    elapsed = time.time() - start_time

    print(f"\nTraining complete in {elapsed:.1f} seconds")

    
    # Save model
    

    model_path = os.path.join(
        BEST_MODEL_DIR,
        "rf3_final_model.pkl"
    )

    joblib.dump(model, model_path)

    print(f"Model saved → {model_path}")

    
    # Save class distribution
    

    dist_lines = []

    total = len(y_all)

    for class_id, class_name in CLASS_NAMES.items():

        count = int(np.sum(y_all == class_id))

        pct = count / total * 100

        dist_lines.append(
            f"{class_id},"
            f"{class_name},"
            f"{count},"
            f"{pct:.4f}"
        )

    dist_path = os.path.join(
        RESULTS_DIR,
        "rf3_final_class_distribution.txt"
    )

    with open(dist_path, "w") as f:

        f.write(
            "class_id,class_name,pixel_count,percentage\n"
        )

        f.write("\n".join(dist_lines))



    
    # Final summary
    

    print("Saved files:")
    print(f"  Model  : {model_path}")
    print(f"  Scaler : {scaler_path}")


    print(f"model = joblib.load(r'{model_path}')")
    print(f"scaler = joblib.load(r'{scaler_path}')")

    print("X_new_scaled = scaler.transform(X_new)")
    print("predictions = model.predict(X_new_scaled)")



if __name__ == "__main__":
    main()