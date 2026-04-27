import rasterio
import numpy as np
from rasterio.warp import reproject, Resampling


# ===============================
# 1. Load raster with profile
# ===============================
def load_raster(path):
    with rasterio.open(path) as src:
        return src.read(1), src.profile


# ===============================
# 2. Align raster to reference
# ===============================
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



# Load ALL datasets

def load_all_data():

    # --- LAND COVER (reference grid) ---
    land_2020, ref_profile = load_raster("../data/landcover/norwich_landcover_2020.tif")
    land_2021, _ = load_raster("../data/landcover/norwich_landcover_2021.tif")

    # --- OTHER DATASETS ---
    ndvi, ndvi_profile = load_raster("../data/ndvi/norwich_ndvi.tif")
    elevation, elev_profile = load_raster("../data/elevation/norwich_elevation.tif")
    population, pop_profile = load_raster("../data/population/norwich_population.tif")
    temperature, temp_profile = load_raster("../data/temperature/norwich_temperature.tif")
    water_dist, water_profile = load_raster("../data/distance/norwich_distwater.tif")

    # ===============================
    # 4. ALIGN EVERYTHING
    # ===============================
    ndvi = align_to_ref(ndvi, ndvi_profile, ref_profile)
    elevation = align_to_ref(elevation, elev_profile, ref_profile)
    population = align_to_ref(population, pop_profile, ref_profile)
    temperature = align_to_ref(temperature, temp_profile, ref_profile)
    water_dist = align_to_ref(water_dist, water_profile, ref_profile)

    # ===============================
    # 5. PRINT SHAPES (sanity check)
    # ===============================
    print("All aligned shapes:")
    print("Land 2020:", land_2020.shape)
    print("NDVI:", ndvi.shape)
    print("Elevation:", elevation.shape)
    print("Population:", population.shape)
    print("Temperature:", temperature.shape)
    print("Water distance:", water_dist.shape)

    # ===============================
    # 6. STACK FEATURES (X)
    # ===============================
    X = np.stack([
        ndvi,
        elevation,
        population,
        temperature,
        water_dist
    ], axis=-1)

    # ===============================
    # 7. TARGET (y)
    # ===============================
    y = (land_2021 != land_2020).astype(np.uint8)

    return X, y, ref_profile


# ===============================
# 8. RUN SCRIPT
# ===============================
if __name__ == "__main__":
    X, y, profile = load_all_data()

    print("\nFinal dataset:")
    print("X shape:", X.shape)
    print("y shape:", y.shape)