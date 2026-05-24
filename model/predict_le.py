import os
import warnings
import matplotlib
matplotlib.use("Agg")  

import joblib
import numpy as np
import rasterio
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
from scipy.ndimage import generic_filter

warnings.filterwarnings("ignore")



# CONFIG

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR       = os.path.join(BASE_DIR, "processed_data")
BEST_MODEL_DIR = os.path.join(BASE_DIR, "best_model")
OUTPUT_DIR     = os.path.join(BASE_DIR, "forecasts")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Historical snapshots used to fit trends
HISTORICAL_YEARS = [1985, 1995, 2005, 2015, 2024]

# Future years to forecast (10 year intervals, 100 years ahead)
FUTURE_YEARS = [2034, 2044, 2054, 2064, 2074, 2084, 2094, 2104, 2114, 2124]

NODATA_LABEL = 255
NODATA_PRED  = 255

CLASS_NAMES = {
    0: "Vegetation",
    1: "Agricultural",
    2: "Urban",
    3: "Water",
    4: "Sparse",
}

CLASS_COLOURS = {
    0: "#2e7d32",   # Vegetation   — green
    1: "#fdd835",   # Agricultural — yellow
    2: "#d32f2f",   # Urban        — red
    3: "#1565c0",   # Water        — blue
    4: "#8d6e63",   # Sparse       — brown
}

# Features that change over time (fitted with linear trend)
DYNAMIC_FEATURES = ["rgb", "ndvi", "temperature", "population"]

# Features that are static (carried forward unchanged)
STATIC_FEATURES  = ["elevation", "distance_to_water"]


POPULATION_SNAP_MAP = {
    1985: 2000,
    1995: 2000,
    2005: 2000,
    2015: 2010,
    2024: 2020,
}
# The three unique population years (used for the 3 point re-fit)
POPULATION_YEARS = [2000, 2010, 2020]



# RASTER LOADER


def load_raster(path: str) -> np.ndarray:
    with rasterio.open(path) as src:
        data = src.read()
    return data.astype(np.float32)


def get_profile(path: str) -> dict:
    with rasterio.open(path) as src:
        return src.profile.copy()



# LOAD ALL HISTORICAL FEATURE STACKS

# Returns a dict: year -> (H*W, F) array of all valid+invalid pixels



def load_all_historical(reference_year: int = 2024):

    """
    Load every historical snapshot into a dict of flat feature arrays.

    Returns
    all_X        : {year: np.ndarray (H*W, F)}  — full flat arrays
    labels       : {year: np.ndarray (H*W,)}    — flat label arrays
    H, W         : raster dimensions
    F            : number of features
    profile      : rasterio profile (from reference year labels)
    valid_mask   : (H*W,) bool — pixels valid in ALL years (label NoData
                   intersection only — no footprint heuristic that leaks
                   border pixels through elevation/water which are nonzero
                   everywhere in the bounding box)
    pop_col_start: int — index of the first population feature column,
                   needed for the 3-point population trend re-fit
    pop_n_bands  : int — number of population bands
    all_X_pop    : {pop_year: (H*W, pop_n_bands)} — raw population arrays
                   keyed by the three genuine WorldPop years, used to
                   re-fit population trends correctly
    """

    print("Loading all historical snapshots...")

    all_X    = {}
    labels   = {}
    H = W = F = None
    profile  = None


    all_X_pop   = {}
    pop_col_start = None
    pop_n_bands   = None

    for year in HISTORICAL_YEARS:

        print(f"  {year}...")

        rgb       = load_raster(os.path.join(DATA_DIR, f"rgb_{year}.tif"))
        ndvi      = load_raster(os.path.join(DATA_DIR, f"ndvi_{year}.tif"))
        temp      = load_raster(os.path.join(DATA_DIR, f"temperature_{year}.tif"))
        elevation = load_raster(os.path.join(DATA_DIR, "elevation.tif"))
        water     = load_raster(os.path.join(DATA_DIR, "distance_to_water.tif"))

        label_path = os.path.join(DATA_DIR, f"labels_{year}.tif")
        lbl = load_raster(label_path)[0]

        if year == reference_year:
            profile = get_profile(label_path)

        pop_year   = POPULATION_SNAP_MAP[year]
        population = load_raster(os.path.join(DATA_DIR, f"population_{pop_year}.tif"))

        feature_list = []
        for i in range(rgb.shape[0]):
            feature_list.append(rgb[i])
        for i in range(ndvi.shape[0]):
            feature_list.append(ndvi[i])
        for i in range(temp.shape[0]):
            feature_list.append(temp[i])

        # Record where the population columns start (only need to do this once)
        if pop_col_start is None:
            pop_col_start = len(feature_list)
            pop_n_bands   = population.shape[0]

        for i in range(population.shape[0]):
            feature_list.append(population[i])
        feature_list.append(elevation[0])
        feature_list.append(water[0])

        X_full = np.stack(feature_list, axis=-1)   # (H, W, F)
        H_yr, W_yr, F_yr = X_full.shape

        if H is None:
            H, W, F = H_yr, W_yr, F_yr

        all_X[year]  = X_full.reshape(-1, F)       # (H*W, F)
        labels[year] = lbl.reshape(-1)              # (H*W,)

        # Store population rasters keyed by their genuine year so we can
        # re-fit on 3 distinct points later. We only need to store each
        # unique population year once.
        if pop_year not in all_X_pop:
            pop_flat = np.stack(
                [population[i].reshape(-1) for i in range(population.shape[0])],
                axis=-1,
            )  # (H*W, pop_n_bands)
            all_X_pop[pop_year] = pop_flat


    valid_mask = np.ones(H * W, dtype=bool)
    for year in HISTORICAL_YEARS:
        y_flat = labels[year]
        valid_mask &= (y_flat >= 0) & (y_flat != NODATA_LABEL)

    print(f"  Valid pixels (all years): {valid_mask.sum():,} / {H*W:,}")
    print(f"  Features: {F}")
    print(f"  Population columns: {pop_col_start} to {pop_col_start + pop_n_bands - 1}")

    return (
        all_X, labels, H, W, F, profile, valid_mask,
        pop_col_start, pop_n_bands, all_X_pop,
    )



# FIT PIXEL-WISE LINEAR TRENDS


def fit_pixel_trends(
    all_X: dict,
    F: int,
    valid_mask: np.ndarray,
    pop_col_start: int,
    pop_n_bands: int,
    all_X_pop: dict,
):


    N = list(all_X.values())[0].shape[0]
    years = np.array(HISTORICAL_YEARS, dtype=np.float64)

    # Stack historical observations: shape (T, N, F)
    X_stack = np.stack([all_X[y] for y in HISTORICAL_YEARS], axis=0)

    print("Fitting pixel-wise linear trends (all features)...")

    # Vectorised closed-form OLS: centre years for numerical stability
    T      = len(years)
    y_mean = years.mean()
    x_vals = years - y_mean          # (T,)
    denom  = (x_vals ** 2).sum()     # scalar

    X_mean    = X_stack.mean(axis=0)                                            # (N, F)
    x_centred = X_stack - X_mean[np.newaxis, :, :]                             # (T, N, F)
    numerator = (x_vals[:, np.newaxis, np.newaxis] * x_centred).sum(axis=0)    # (N, F)

    slopes     = (numerator / denom).astype(np.float32)
    intercepts = (X_mean - slopes * y_mean).astype(np.float32)


    print("  Re-fitting population columns with 3-point OLS...")

    pop_years_arr = np.array(POPULATION_YEARS, dtype=np.float64)   # [2000, 2010, 2020]
    py_mean  = pop_years_arr.mean()
    px_vals  = pop_years_arr - py_mean
    p_denom  = (px_vals ** 2).sum()

    # Stack the 3 genuine population rasters: (3, N, pop_n_bands)
    pop_stack = np.stack(
        [all_X_pop[py] for py in POPULATION_YEARS], axis=0
    )

    p_X_mean    = pop_stack.mean(axis=0)                                                
    p_x_centred = pop_stack - p_X_mean[np.newaxis, :, :]                               
    p_numerator = (px_vals[:, np.newaxis, np.newaxis] * p_x_centred).sum(axis=0)       

    pop_slopes     = (p_numerator / p_denom).astype(np.float32)
    pop_intercepts = (p_X_mean - pop_slopes * py_mean).astype(np.float32)

    # Overwrite the population columns in the main slope/intercept arrays
    pop_col_end = pop_col_start + pop_n_bands
    slopes    [:, pop_col_start:pop_col_end] = pop_slopes
    intercepts[:, pop_col_start:pop_col_end] = pop_intercepts

    print("  Done.")
    return slopes, intercepts



# PROJECT FEATURE STACK TO A FUTURE YEAR


def project_features(
    slopes: np.ndarray,
    intercepts: np.ndarray,
    all_X: dict,
    future_year: int,
    F: int,
    static_feature_indices: list,
    valid_mask: np.ndarray,
):
    """
    Build projected feature matrix for a single future year.

    Static features (elevation, distance_to_water) are copied from
    the most recent historical snapshot rather than extrapolated.

    Clipping is computed over valid pixels only to prevent the
    all zero border pixels from collapsing feat_min to zero.
    """

    X_proj = intercepts + slopes * future_year     # (N, F)

    X_proj[~valid_mask] = 0.0

    # Overwrite static feature columns with 2024 values
    X_2024 = all_X[2024]
    for idx in static_feature_indices:
        X_proj[:, idx] = X_2024[:, idx]

    # Clip each feature to the range observed across VALID pixels only.

    X_stack       = np.stack(list(all_X.values()), axis=0)   # (T, N, F)
    X_valid_stack = X_stack[:, valid_mask, :]                  # (T, N_valid, F)
    feat_min = X_valid_stack.min(axis=(0, 1))                  # (F,)
    feat_max = X_valid_stack.max(axis=(0, 1))                  # (F,)
    X_proj[valid_mask] = np.clip(X_proj[valid_mask], feat_min, feat_max)

    # Force pixels outside the study footprint to zero so they stay masked.

    X_proj[~valid_mask] = 0.0

    return X_proj.astype(np.float32)



# MAJORITY FILTER



def majority_filter(pred_map: np.ndarray, size: int = 3) -> np.ndarray:

    """
    Apply a spatial majority filter to a predicted land cover map.

    NoData pixels are excluded from voting and restored afterwards.

    """
    nodata_mask = pred_map == NODATA_PRED

    def modal(values):
        # Use np.bincount to find the most common class value.
        # Exclude NODATA (255) from voting by only counting values < 255.
        # scipy.stats.mode is broken inside generic_filter in newer scipy.
        ints = values.astype(np.int32)
        valid = ints[ints < NODATA_PRED]
        if len(valid) == 0:
            return float(NODATA_PRED)
        return float(np.bincount(valid).argmax())

    # generic_filter passes a flat neighbourhood array to the function
    smoothed = generic_filter(
        pred_map.astype(np.float64), modal, size=size, mode="nearest"
    ).astype(np.uint8)

    # Restore NoData pixels that may have been overwritten by the filter
    smoothed[nodata_mask] = NODATA_PRED

    return smoothed



# SAVE GEOTIFF


def save_geotiff(array: np.ndarray, profile: dict, path: str):
    p = profile.copy()
    p.update(dtype=rasterio.uint8, count=1, nodata=NODATA_PRED)
    with rasterio.open(path, "w", **p) as dst:
        dst.write(array[np.newaxis, :, :])
    print(f"    GeoTIFF saved → {path}")



# VISUALISE SINGLE FORECAST YEAR


def visualise_forecast(pred_map, year, output_dir):

    n_classes = len(CLASS_NAMES)

    colours = [
        CLASS_COLOURS[i]
        for i in range(n_classes)
    ]

    cmap = ListedColormap(colours)

    display = np.ma.masked_equal(
        pred_map,
        NODATA_PRED
    )

    fig, ax = plt.subplots(
        figsize=(8, 8)
    )

    fig.patch.set_alpha(0)

    ax.set_facecolor(
        (0, 0, 0, 0)
    )

    ax.imshow(
        display,
        cmap=cmap,
        vmin=0,
        vmax=n_classes - 1,
        interpolation="nearest"
    )

    ax.axis("off")

    plt.subplots_adjust(
        left=0,
        right=1,
        top=1,
        bottom=0
    )

    out = os.path.join(
        output_dir,
        f"forecast_{year}.png"
    )

    plt.savefig(
        out,
        transparent=True,
        bbox_inches="tight",
        pad_inches=0,
        dpi=300
    )

    plt.close()

    print(
        f"Overlay PNG saved to {out}"
    )



# MAIN


def main():


    # Load model and scaler


    model  = joblib.load(os.path.join(BEST_MODEL_DIR, "rf3_final_model.pkl"))
    scaler = joblib.load(os.path.join(BEST_MODEL_DIR, "rf3_final_scaler.pkl"))



    # Load all historical feature stacks

    (
        all_X, labels, H, W, F, profile, valid_mask,
        pop_col_start, pop_n_bands, all_X_pop,
    ) = load_all_historical()

    # Identify static feature column indices.

    # Elevation and distance_to_water are the last two columns.

    static_feature_indices = [F - 2, F - 1]


    # Fit pixel-wise linear trends across historical years
    # (population columns refitted on 3 genuine observations)

    slopes, intercepts = fit_pixel_trends(
        all_X, F, valid_mask,
        pop_col_start, pop_n_bands, all_X_pop,
    )


    # Generate historical prediction maps (for timeline figure)

    print("\nGenerating historical prediction maps for timeline...")
    historical_maps = {}

    for year in HISTORICAL_YEARS:
        X_year   = all_X[year]
        X_valid  = X_year[valid_mask]
        X_scaled = scaler.transform(X_valid)
        preds    = model.predict(X_scaled).astype(np.uint8)

        pred_flat             = np.full(H * W, NODATA_PRED, dtype=np.uint8)
        pred_flat[valid_mask] = preds
        historical_maps[year] = pred_flat.reshape(H, W)

        print(f"  {year} done.")


    # Generate future forecasts


    forecast_maps = {}

    for future_year in FUTURE_YEARS:

        print(f"Forecasting {future_year}...")

        # Project feature stack to future year
        X_proj = project_features(
            slopes, intercepts, all_X,
            future_year, F, static_feature_indices,
            valid_mask,
        )

        # Extract valid pixels only
        X_valid  = X_proj[valid_mask]
        X_scaled = scaler.transform(X_valid)
        preds    = model.predict(X_scaled).astype(np.uint8)

        # Reconstruct raster
        pred_flat             = np.full(H * W, NODATA_PRED, dtype=np.uint8)
        pred_flat[valid_mask] = preds
        pred_map              = pred_flat.reshape(H, W)

        print(f"Applying majority filter...")
        pred_map = majority_filter(pred_map, size=3)

        forecast_maps[future_year] = pred_map

        # Export GeoTIFF
        save_geotiff(
            pred_map, profile,
            os.path.join(OUTPUT_DIR, f"forecast_{future_year}.tif"),
        )

        # Export individual figure
        visualise_forecast(pred_map, future_year, OUTPUT_DIR)

        print()


    print("FORECASTING COMPLETE")

    print(f"\nAll outputs saved to: {OUTPUT_DIR}\n")



if __name__ == "__main__":
    main()