import rasterio
import numpy as np
from rasterio.warp import reproject, Resampling
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_raster(path):
    with rasterio.open(path) as src:
        return src.read(1), src.profile


def align_to_ref(source_array, source_profile, ref_profile, method="bilinear"):
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


def clean_ndvi(arr):
    if np.isnan(arr).all():
        return np.zeros_like(arr)
    return np.nan_to_num(arr, nan=np.nanmean(arr))


def clean_generic(arr):
    return np.nan_to_num(arr, nan=np.nanmax(arr))


def normalize(arr):
    min_val = np.min(arr)
    max_val = np.max(arr)

    if max_val - min_val == 0:
        return arr

    return (arr - min_val) / (max_val - min_val)


def process_year(year, ref_profile):
    ndvi, ndvi_profile = load_raster(
        os.path.join(DATA_DIR, f"ndvi/norwich_ndvi_{year}.tif")
    )
    pop, pop_profile = load_raster(
        os.path.join(DATA_DIR, f"population/norwich_population_{year}.tif")
    )
    temp, temp_profile = load_raster(
        os.path.join(DATA_DIR, f"temperature/norwich_temperature_{year}.tif")
    )

    ndvi = align_to_ref(ndvi, ndvi_profile, ref_profile)
    pop = align_to_ref(pop, pop_profile, ref_profile)
    temp = align_to_ref(temp, temp_profile, ref_profile)

    ndvi = normalize(clean_ndvi(ndvi))
    pop = normalize(clean_generic(pop))
    temp = normalize(clean_generic(temp))

    return ndvi, pop, temp


def load_static(ref_profile):
    elev, elev_profile = load_raster(
        os.path.join(DATA_DIR, "elevation/norwich_elevation.tif")
    )
    water, water_profile = load_raster(
        os.path.join(DATA_DIR, "distance/norwich_distwater.tif")
    )

    elev = normalize(clean_generic(align_to_ref(elev, elev_profile, ref_profile)))
    water = normalize(clean_generic(align_to_ref(water, water_profile, ref_profile)))

    return elev, water


def load_all_data():

    years = [2016, 2017, 2018, 2019, 2020]

    land_0, ref_profile = load_raster(
        os.path.join(DATA_DIR, f"dynamicworld/norwich_dynamicworld_{years[0]}.tif")
    )

    elevation, water = load_static(ref_profile)

    X_list = []
    y_list = []

    for i in range(len(years) - 1):

        y1 = years[i]
        y2 = years[i + 1]

        print(f"Processing: {y1} -> {y2}")

        ndvi, pop, temp = process_year(y1, ref_profile)

        X = np.stack([ndvi, pop, temp, elevation, water], axis=-1)

        land_t, _ = load_raster(
            os.path.join(DATA_DIR, f"dynamicworld/norwich_dynamicworld_{y1}.tif")
        )
        land_t1, _ = load_raster(
            os.path.join(DATA_DIR, f"dynamicworld/norwich_dynamicworld_{y2}.tif")
        )

        y = (land_t1 != land_t).astype(np.uint8)

        X_list.append(X)
        y_list.append(y)

    X_final = np.concatenate(X_list, axis=0)
    y_final = np.concatenate(y_list, axis=0)

    print("\nFinal dataset:")
    print("X shape:", X_final.shape)
    print("y shape:", y_final.shape)
    print("NaNs:", np.isnan(X_final).sum())

    return X_final, y_final, ref_profile


if __name__ == "__main__":
    load_all_data()