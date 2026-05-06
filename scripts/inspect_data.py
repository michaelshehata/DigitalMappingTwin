import rasterio
import numpy as np
import os
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def inspect(path, name):
    with rasterio.open(path) as src:
        data = src.read(1)

        print(f"\n=== {name} ===")
        print("Shape:", data.shape)
        print("Min:", np.nanmin(data))
        print("Max:", np.nanmax(data))
        print("Mean:", np.nanmean(data))
        print("NaNs:", np.isnan(data).sum())

        plt.figure(figsize=(6, 4))
        plt.imshow(data, cmap="viridis")
        plt.title(name)
        plt.colorbar()

        save_path = os.path.join(OUTPUT_DIR, f"{name.replace(' ', '_')}.png")
        plt.savefig(save_path, dpi=300)
        plt.show()

        print("Saved image:", save_path)


def main():

    inspect(os.path.join(DATA_DIR, "dynamicworld/norwich_dynamicworld_2018.tif"), "Landcover 2018")

    inspect(os.path.join(DATA_DIR, "ndvi/norwich_ndvi_2018.tif"), "NDVI 2018")
    inspect(os.path.join(DATA_DIR, "population/norwich_population_2018.tif"), "Population 2018")
    inspect(os.path.join(DATA_DIR, "temperature/norwich_temperature_2018.tif"), "Temperature 2018")

    inspect(os.path.join(DATA_DIR, "elevation/norwich_elevation.tif"), "Elevation")
    inspect(os.path.join(DATA_DIR, "distance/norwich_distwater.tif"), "Distance to Water")


if __name__ == "__main__":
    main()