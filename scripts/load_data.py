import rasterio
import numpy as np
from rasterio.warp import reproject, Resampling
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_raster(path):
    """Load single band raster file"""
    with rasterio.open(path) as src:
        data = src.read()

        # Handle multiband rasters
        if data.shape[0] == 1:
            data = data[0]
        else:
            # Convert from (bands, height, width)
            # to (height, width, bands)
            data = np.transpose(data, (1, 2, 0))

        return data.astype(np.float32), src.profile


def align_to_ref(source_array, source_profile, ref_profile, method="bilinear"):
    """Reproject and resample raster to reference grid"""

    # MULTIBAND
    if source_array.ndim == 3:

        aligned_bands = []

        for i in range(source_array.shape[2]):

            aligned = np.empty(
                (ref_profile['height'], ref_profile['width']),
                dtype=np.float32
            )

            resampling_method = {
                "bilinear": Resampling.bilinear,
                "nearest": Resampling.nearest
            }[method]

            reproject(
                source_array[:, :, i],
                aligned,
                src_transform=source_profile['transform'],
                src_crs=source_profile['crs'],
                dst_transform=ref_profile['transform'],
                dst_crs=ref_profile['crs'],
                resampling=resampling_method
            )

            aligned_bands.append(aligned)

        return np.stack(aligned_bands, axis=-1)

    # SINGLE BAND
    else:

        aligned = np.empty(
            (ref_profile['height'], ref_profile['width']),
            dtype=np.float32
        )

        resampling_method = {
            "bilinear": Resampling.bilinear,
            "nearest": Resampling.nearest
        }[method]

        reproject(
            source_array,
            aligned,
            src_transform=source_profile['transform'],
            src_crs=source_profile['crs'],
            dst_transform=ref_profile['transform'],
            dst_crs=ref_profile['crs'],
            resampling=resampling_method
        )

        return aligned


def interpolate_population(pop_2000, pop_2010, pop_2020, target_year):
    """Linear interpolation of population"""

    if target_year <= 2000:
        return pop_2000

    elif target_year <= 2010:
        weight = (target_year - 2000) / 10.0
        return pop_2000 * (1 - weight) + pop_2010 * weight

    elif target_year <= 2020:
        weight = (target_year - 2010) / 10.0
        return pop_2010 * (1 - weight) + pop_2020 * weight

    else:
        extrapolate_weight = (target_year - 2020) / 10.0
        growth_rate = pop_2020 - pop_2010
        return pop_2020 + growth_rate * extrapolate_weight


def clean_ndvi(arr):
    """Clean NDVI using mean imputation"""

    if np.isnan(arr).all():
        return np.zeros_like(arr)

    return np.nan_to_num(arr, nan=np.nanmean(arr))


def clean_generic(arr):
    """Generic NaN cleaning"""

    if np.isnan(arr).all():
        return np.zeros_like(arr)

    return np.nan_to_num(arr, nan=np.nanmean(arr))


def normalize(arr):
    """Min-max normalization"""

    min_val = np.nanmin(arr)
    max_val = np.nanmax(arr)

    if max_val - min_val == 0:
        return arr

    return (arr - min_val) / (max_val - min_val)


def compute_ndbi(swir, nir):
    """Compute NDBI"""

    denominator = swir + nir + 1e-8
    return (swir - nir) / denominator


def compute_spectral_change(rgb1, rgb2):
    """
    Spectral change detection using RGB composites
    """

    # RGB channels
    r1 = rgb1[:, :, 0]
    g1 = rgb1[:, :, 1]
    b1 = rgb1[:, :, 2]

    r2 = rgb2[:, :, 0]
    g2 = rgb2[:, :, 1]
    b2 = rgb2[:, :, 2]

    # Pseudo NDVI
    ndvi1 = (g1 - r1) / (g1 + r1 + 1e-8)
    ndvi2 = (g2 - r2) / (g2 + r2 + 1e-8)

    # Spectral difference
    spectral_diff = np.sqrt(
        (r2 - r1) ** 2 +
        (g2 - g1) ** 2 +
        (b2 - b1) ** 2
    )

    # NDVI difference
    ndvi_diff = np.abs(ndvi2 - ndvi1)

    # Combined change metric
    combined_change = (
        0.7 * spectral_diff +
        0.3 * ndvi_diff
    )

    return combined_change


def process_year(year, pop_cache, ref_profile):
    """Process all dynamic features for a single year"""

    ndvi, ndvi_profile = load_raster(
        os.path.join(DATA_DIR, f"ndvi/ndvi_{year}.tif")
    )

    temp, temp_profile = load_raster(
        os.path.join(DATA_DIR, f"temperature/temperature_{year}.tif")
    )

    ndvi = align_to_ref(
        ndvi,
        ndvi_profile,
        ref_profile,
        method="bilinear"
    )

    temp = align_to_ref(
        temp,
        temp_profile,
        ref_profile,
        method="bilinear"
    )

    ndvi = normalize(clean_ndvi(ndvi))
    temp = normalize(clean_generic(temp))

    if year in pop_cache:
        pop = pop_cache[year]
    else:
        pop = np.zeros_like(ndvi)

    return ndvi, pop, temp


def load_all_data(years=None):
    """Load and preprocess all datasets"""

    if years is None:
        years = [1985, 1995, 2005, 2015, 2024]

    print(f"Loading data for years: {years}")

    # REFERENCE GRID
    ndvi_ref, ref_profile = load_raster(
        os.path.join(DATA_DIR, f"ndvi/ndvi_{years[0]}.tif")
    )

    # STATIC FEATURES
    elevation, elev_profile = load_raster(
        os.path.join(DATA_DIR, "elevation/elevation.tif")
    )

    water, water_profile = load_raster(
        os.path.join(DATA_DIR, "water/distance_to_water.tif")
    )

    elevation = align_to_ref(
        elevation,
        elev_profile,
        ref_profile
    )

    water = align_to_ref(
        water,
        water_profile,
        ref_profile
    )

    elevation = normalize(clean_generic(elevation))
    water = normalize(clean_generic(water))

    # POPULATION
    pop_years = [2000, 2010, 2020]
    pop_data = {}

    for py in pop_years:

        pop_arr, pop_profile = load_raster(
            os.path.join(DATA_DIR, f"population/population_{py}.tif")
        )

        pop_arr = align_to_ref(
            pop_arr,
            pop_profile,
            ref_profile,
            method="bilinear"
        )

        pop_data[py] = normalize(clean_generic(pop_arr))

    pop_cache = {}

    for year in years:

        if year in pop_data:

            pop_cache[year] = pop_data[year]

        else:

            pop_cache[year] = interpolate_population(
                pop_data[2000],
                pop_data[2010],
                pop_data[2020],
                year
            )

            pop_cache[year] = normalize(pop_cache[year])

    # LANDCOVER
    landcover_data = {}

    for year in years:

        lc_arr, lc_profile = load_raster(
            os.path.join(DATA_DIR, f"landcover/landcover_{year}.tif")
        )

        lc_arr = align_to_ref(
            lc_arr,
            lc_profile,
            ref_profile,
            method="bilinear"
        )

        lc_arr = clean_generic(lc_arr)

        landcover_data[year] = lc_arr

    X_list = []
    y_list = []

    for i in range(len(years) - 1):

        y1 = years[i]
        y2 = years[i + 1]

        print(f"Processing transition: {y1} → {y2}")

        ndvi_t1, pop_t1, temp_t1 = process_year(
            y1,
            pop_cache,
            ref_profile
        )

        # FEATURE STACK
        X = np.stack([
            ndvi_t1,
            pop_t1,
            temp_t1,
            elevation,
            water
        ], axis=-1)

        # LANDCOVER CHANGE
        lc_t1 = landcover_data[y1]
        lc_t2 = landcover_data[y2]

        spectral_change = compute_spectral_change(
            lc_t1,
            lc_t2
        )

        spectral_change = normalize(spectral_change)

        # CHANGE THRESHOLD
        CHANGE_THRESHOLD = 0.20

        y = (
            spectral_change > CHANGE_THRESHOLD
        ).astype(np.uint8)

        X_list.append(X)
        y_list.append(y)

    # PRESERVE TEMPORAL DIMENSION
    X_final = np.stack(X_list, axis=0)
    y_final = np.stack(y_list, axis=0)

    # SUMMARY
    print("\nFINAL DATASET SUMMARY")
    print("=" * 50)

    print(f"X shape: {X_final.shape}")
    print(f"y shape: {y_final.shape}")

    print(f"NaNs in X: {np.isnan(X_final).sum()}")

    print("\nFeature ranges:")
    print(f"  NDVI: [{X_final[..., 0].min():.3f}, {X_final[..., 0].max():.3f}]")
    print(f"  Pop:  [{X_final[..., 1].min():.3f}, {X_final[..., 1].max():.3f}]")
    print(f"  Temp: [{X_final[..., 2].min():.3f}, {X_final[..., 2].max():.3f}]")
    print(f"  Elev: [{X_final[..., 3].min():.3f}, {X_final[..., 3].max():.3f}]")
    print(f"  Water:[{X_final[..., 4].min():.3f}, {X_final[..., 4].max():.3f}]")

    unique, counts = np.unique(y_final, return_counts=True)

    print("\nClass distribution:")

    for u, c in zip(unique, counts):

        percentage = 100 * c / y_final.size

        print(f"  Class {u}: {c} ({percentage:.2f}%)")

    print("=" * 50)

    return X_final, y_final, ref_profile


if __name__ == "__main__":

    X, y, profile = load_all_data()