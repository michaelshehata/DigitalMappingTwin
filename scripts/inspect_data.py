import rasterio
import numpy as np
import os
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def inspect(path, name, cmap="viridis"):
    """Inspect and visualize a single raster file"""
    try:
        with rasterio.open(path) as src:
            data = src.read(1)

            print(f"\n{'='*50}")
            print(f"  {name}")
            print(f"{'='*50}")
            print(f"Shape:          {data.shape}")
            print(f"Data Type:      {data.dtype}")
            print(f"Min:            {np.nanmin(data):.6f}")
            print(f"Max:            {np.nanmax(data):.6f}")
            print(f"Mean:           {np.nanmean(data):.6f}")
            print(f"Std Dev:        {np.nanstd(data):.6f}")
            print(f"NaNs:           {np.isnan(data).sum()} ({100*np.isnan(data).sum()/data.size:.2f}%)")
            print(f"{'='*50}")

            plt.figure(figsize=(8, 6))
            im = plt.imshow(data, cmap=cmap)
            plt.title(f"{name}\nMin: {np.nanmin(data):.2f} | Max: {np.nanmax(data):.2f}", fontsize=12)
            plt.colorbar(im, label="Value")

            save_path = os.path.join(OUTPUT_DIR, f"{name.replace(' ', '_').replace('/', '_')}.png")
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            plt.close()

            print(f"Visualization saved: {save_path}\n")

    except FileNotFoundError:
        print(f"\nFile not found: {path}\n")
    except Exception as e:
        print(f"\nError reading {name}: {str(e)}\n")


def main():
    print("DATA INSPECTION")

    ndvi_years = [1985, 1995, 2005, 2015, 2024]
    temp_years = [1985, 1995, 2005, 2015, 2024]
    pop_years = [2000, 2010, 2020]
    lc_years = [1985, 1995, 2005, 2015, 2024]


    print("NDVI (Vegetation Index)")

    for year in ndvi_years:
        inspect(
            os.path.join(DATA_DIR, f"ndvi/ndvi_{year}.tif"),
            f"NDVI {year}",
            cmap="RdYlGn"
        )


    print("TEMPERATURE (ERA5-Land)")

    for year in temp_years:
        inspect(
            os.path.join(DATA_DIR, f"temperature/temperature_{year}.tif"),
            f"Temperature {year}",
            cmap="RdBu_r"
        )


    print("POPULATION (WorldPop)")

    for year in pop_years:
        inspect(
            os.path.join(DATA_DIR, f"population/population_{year}.tif"),
            f"Population {year}",
            cmap="YlOrRd"
        )


    print("LAND COVER (Landsat RGB)")

    for year in lc_years:
        inspect(
            os.path.join(DATA_DIR, f"landcover/landcover_{year}.tif"),
            f"Landcover {year}",
            cmap="Spectral"
        )


    print("STATIC FEATURES")

    inspect(
        os.path.join(DATA_DIR, "elevation/elevation.tif"),
        "Elevation (SRTM)",
        cmap="terrain"
    )

    inspect(
        os.path.join(DATA_DIR, "water/distance_to_water.tif"),
        "Distance to Water (JRC)",
        cmap="Blues"
    )


    print("INSPECTION COMPLETE")

if __name__ == "__main__":
    main()