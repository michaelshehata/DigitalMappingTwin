"""
All outputs match:
- elevation.tif CRS
- dimensions
- transform
- bounds
"""

import os
import numpy as np
import rasterio

from rasterio.enums import Resampling



# PATHS


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_LCM_DIR = os.path.join(BASE_DIR, "data", "lcm")

PROCESSED_DIR = os.path.join(
    BASE_DIR,
    "processed_data"
)

REFERENCE_RASTER = os.path.join(
    PROCESSED_DIR,
    "elevation.tif"
)

os.makedirs(RAW_LCM_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)



# SNAPSHOT MAPPING


SNAPSHOT_MAP = {

    1985: "lcm1990_25m_gb.tif",

    1995: "lcm1990_25m_gb.tif",  #Temporal gap due to problems with LCM2000 data

    2005: "lcm2007_25m_gb.tif",

    2015: "lcm2015_25m_gb.tif",

    2024: "lcm2023_25m_gb.tif",
}



# OUTPUT CLASSES


CLASS_LABELS = {

    0: "Vegetation",

    1: "Agricultural",

    2: "Urban",

    3: "Water",

    4: "Sparse", # Non vegetated surfaces (bare soil, rock)
}


NODATA_VALUE = 255




LCM_REMAP_STANDARD = {

    1: 0,
    2: 0,

    3: 1,
    4: 1,

    5: 0,
    6: 0,
    7: 0,
    8: 0,
    9: 0,
    10: 0,

    11: 4,
    12: 4,

    13: 3,
    14: 3,

    15: 4,
    16: 4,
    17: 4,
    18: 4,

    19: 0,

    20: 2,
    21: 2,
}



# LCM2000 REMAP
# THIS HAS BEEN SCRAPPED, BUT JUST TO SHOW THE DIFFERENCE IN CLASS NUMBERING SCHEME

LCM_REMAP_2000 = {
    11:  0,    
    21:  0,    
    41:  1,    
    42:  1,    
    43:  1,    
    51:  1,    
    52:  0,    
    61:  0,    
    71:  0,    
    81:  4,    
    111: 2,    
    131: 3,    
    161: 4,    
    171: 4,    
    172: 0,    
}



# LCM2007 REMAP
# Urban classes changed


LCM_REMAP_2007 = {
    1:  0,    # Broadleaved woodland  -> Vegetation
    2:  0,    # Coniferous woodland   -> Vegetation
    3:  1,    # Arable               -> Agricultural
    4:  1,    # Improved grassland   -> Agricultural
    5:  0,    # Neutral grassland    -> Vegetation
    6:  0,    # Calcareous grassland -> Vegetation
    8:  0,    # Fen/marsh/swamp      -> Vegetation
    9:  0,    # Heather              -> Vegetation
    10: 0,    # Heather grassland    -> Vegetation
    11: 4,    # Bog                  -> Bare
    14: 3,    # Freshwater           -> Water
    15: 4,    # Supralittoral rock   -> Bare
    16: 4,    # Littoral sediment    -> Bare
    18: 4,    # Littoral sediment    -> Bare
    22: 2,    # Urban                -> Urban
    23: 2,    # Suburban             -> Urban
}



# LOAD SPATIAL REFERENCE


def load_reference():

    with rasterio.open(REFERENCE_RASTER) as ref:

        return {

            "crs": ref.crs,

            "transform": ref.transform,

            "width": ref.width,

            "height": ref.height,

            "bounds": ref.bounds,
        }



# CLIP TO NORWICH AREA FROM ORIGINAL 'EAST ENGLAND' + RESAMPLE


def reproject_to_reference(src_path, reference):

    with rasterio.open(src_path) as src:

        window = rasterio.windows.from_bounds(

            left=reference["bounds"].left,

            bottom=reference["bounds"].bottom,

            right=reference["bounds"].right,

            top=reference["bounds"].top,

            transform=src.transform
        )

        data = src.read(

            1,

            window=window,

            out_shape=(
                reference["height"],
                reference["width"]
            ),

            resampling=Resampling.mode
        )

    return data.astype(np.uint8)



# REMAP CLASSES


def remap_classes(data, remap_dict):

    remapped = np.full_like(
        data,
        fill_value=NODATA_VALUE,
        dtype=np.uint8
    )

    for lcm_class, unified_class in remap_dict.items():

        remapped[data == lcm_class] = unified_class

    return remapped



# VALIDATION


def validate_output(output_path, reference):

    with rasterio.open(output_path) as out:

        assert out.transform == reference["transform"]

        assert out.width == reference["width"]

        assert out.height == reference["height"]

    print("    Validation passed — matches reference grid exactly")



# REPORTING


def report_class_distribution(data, snapshot_year):

    valid_pixels = data[data != NODATA_VALUE]

    total = len(valid_pixels)

    print(f"\n    Class distribution for {snapshot_year}:")

    for class_id, class_name in CLASS_LABELS.items():

        count = np.sum(valid_pixels == class_id)

        pct = (
            count / total * 100
            if total > 0 else 0
        )

        bar = "█" * int(pct / 2)  # FOR VISUALIZATION TO QUICKLY ASSESS

        print(
            f"      {class_id} "
            f"{class_name:<15} "
            f"{count:>8} px  "
            f"({pct:5.1f}%)  "
            f"{bar}"
        )

    nodata_count = np.sum(data == NODATA_VALUE)

    print(f"      - NoData         {nodata_count:>8} px")



# PROCESS SNAPSHOT


def process_snapshot(snapshot_year, lcm_filename, reference):

    src_path = os.path.join(
        RAW_LCM_DIR,
        lcm_filename
    )

    if not os.path.exists(src_path):

        print(f"\n  SKIPPED {snapshot_year} — file not found")
        return

    print(f"\n  Processing snapshot {snapshot_year} <- {lcm_filename}")



    # SELECT CORRECT REMAP


    if "2000" in lcm_filename:

        remap_dict = LCM_REMAP_2000

    elif "2007" in lcm_filename:

        remap_dict = LCM_REMAP_2007

    else:

        remap_dict = LCM_REMAP_STANDARD



    # STEP 1


    print("Clipping and resampling")

    reprojected = reproject_to_reference(
        src_path,
        reference
    )

    print(f"Unique classes: {np.unique(reprojected)}")



    # STEP 2


    print("Remapping classes")

    remapped = remap_classes(
        reprojected,
        remap_dict
    )



    # STEP 3


    output_filename = f"labels_{snapshot_year}.tif"

    output_path = os.path.join(
        PROCESSED_DIR,
        output_filename
    )

    with rasterio.open(

        output_path,

        "w",

        driver="GTiff",

        height=reference["height"],

        width=reference["width"],

        count=1,

        dtype=np.uint8,

        crs=reference["crs"],

        transform=reference["transform"],

        nodata=NODATA_VALUE,

    ) as dst:

        dst.write(remapped, 1)





    # STEP 4


    validate_output(
        output_path,
        reference
    )



    # STEP 5


    report_class_distribution(
        remapped,
        snapshot_year
    )



# MAIN


def main():

    print("LCM LABEL PREPROCESSING")


    reference = load_reference()

    print(f"  CRS:        {reference['crs']}")
    print(f"  Resolution: 30m x 30m")
    print(f"  Dimensions: {reference['width']} x {reference['height']}")
    print(f"  Bounds:     {reference['bounds']}")

    print("\nClass scheme:")

    for class_id, class_name in CLASS_LABELS.items():

        print(f"  {class_id} = {class_name}")

    print(f"\nProcessing {len(SNAPSHOT_MAP)} snapshots...")

    for snapshot_year, lcm_filename in SNAPSHOT_MAP.items():

        process_snapshot(
            snapshot_year,
            lcm_filename,
            reference
        )

    print("\nCOMPLETE")




if __name__ == "__main__":

    main()