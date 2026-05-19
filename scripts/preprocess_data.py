import os
import numpy as np
import rasterio

from rasterio.warp import reproject
from rasterio.warp import Resampling

os.environ["PROJ_LIB"] = r".venv\Lib\site-packages\rasterio\proj_data"



DATA_DIR = "data"
OUTPUT_DIR = "processed_data"

os.makedirs(OUTPUT_DIR, exist_ok=True)

REFERENCE_RASTER = os.path.join(
    "elevation",
    "elevation.tif"
)


def normalise(data):
    min_val = np.nanmin(data)
    max_val = np.nanmax(data)

    if max_val - min_val == 0:
        return data

    return (data - min_val) / (max_val - min_val)


def clean_data(data):
    data = data.astype(np.float32)

    data[np.isinf(data)] = np.nan

    mean_value = np.nanmean(data)

    data = np.nan_to_num(
        data,
        nan=mean_value
    )

    return data


def get_resampling_method(filename):
    categorical_keywords = [
        "landcover",
        "classification"
    ]

    for keyword in categorical_keywords:
        if keyword in filename.lower():
            return Resampling.nearest

    return Resampling.bilinear


def get_reference_metadata():
    reference_path = os.path.join(
        DATA_DIR,
        REFERENCE_RASTER
    )

    with rasterio.open(reference_path) as ref:

        return {
            "crs": ref.crs,
            "transform": ref.transform,
            "width": ref.width,
            "height": ref.height
        }


REFERENCE = get_reference_metadata()


def preprocess_raster(filepath):
    filename = os.path.basename(filepath)

    print(f"\nProcessing: {filename}")

    with rasterio.open(filepath) as src:

        metadata = src.meta.copy()

        metadata.update({
            "crs": REFERENCE["crs"],
            "transform": REFERENCE["transform"],
            "width": REFERENCE["width"],
            "height": REFERENCE["height"],
            "dtype": "float32"
        })

        output_path = os.path.join(
            OUTPUT_DIR,
            filename
        )

        with rasterio.open(output_path, "w", **metadata) as dst:

            for band in range(1, src.count + 1):

                source_data = src.read(band)

                destination = np.empty(
                    (
                        REFERENCE["height"],
                        REFERENCE["width"]
                    ),
                    dtype=np.float32
                )

                reproject(
                    source=source_data,
                    destination=destination,
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=REFERENCE["transform"],
                    dst_crs=REFERENCE["crs"],
                    resampling=get_resampling_method(filename)
                )

                destination = clean_data(destination)

                destination = normalise(destination)

                dst.write(
                    destination,
                    band
                )

    print(f"Finished: {filename}")


for root, dirs, files in os.walk(DATA_DIR):
    for filename in files:
        if filename.endswith(".tif"):
            filepath = os.path.join(root, filename)
            preprocess_raster(filepath)

print("\nPreprocessing complete.")