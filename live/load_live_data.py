import os
import requests
import numpy as np
import rasterio

from scripts.load_data import (
    load_raster,
    align_to_ref,
    normalize,
    clean_generic,
    clean_ndvi
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")

LIVE_DIR = os.path.join(BASE_DIR, "live", "data")



# FETCH LIVE TEMPERATURE


def fetch_live_temperature():
    """
    Fetch current Norwich temperature
    using Open-Meteo API
    """

    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=52.6309"
        "&longitude=1.2974"
        "&current=temperature_2m"
    )

    response = requests.get(url)

    data = response.json()

    temperature = data["current"]["temperature_2m"]

    print(f"\nLive temperature: {temperature}°C")

    return temperature


# CREATE TEMPERATURE RASTER


def create_temperature_raster(value, shape):
    """
    Create constant raster from scalar temperature
    """

    return np.full(shape, value, dtype=np.float32)



# LOAD LIVE DATA


def load_live_data():

    print("\nLOADING LIVE DATA")
    print("=" * 50)


    # LIVE NDVI


    ndvi_path = os.path.join(
        LIVE_DIR,
        "ndvi",
        "ndvi_live.tif"
    )

    ndvi, ref_profile = load_raster(ndvi_path)

    ndvi = clean_ndvi(ndvi)

    # Preserve physical NDVI meaning
    # Convert from [-1,1] → [0,1]
    ndvi = (ndvi + 1.0) / 2.0

    ndvi = np.clip(ndvi, 0, 1)

    print(f"Loaded live NDVI: {ndvi.shape}")



    # STATIC ELEVATION


    elevation, elev_profile = load_raster(
        os.path.join(
            DATA_DIR,
            "elevation",
            "elevation.tif"
        )
    )

    elevation = align_to_ref(
        elevation,
        elev_profile,
        ref_profile
    )

    elevation = normalize(
        clean_generic(elevation)
    )



    # STATIC WATER


    water, water_profile = load_raster(
        os.path.join(
            DATA_DIR,
            "water",
            "distance_to_water.tif"
        )
    )

    water = align_to_ref(
        water,
        water_profile,
        ref_profile
    )

    water = normalize(
        clean_generic(water)
    )



    # STATIC POPULATION


    population, pop_profile = load_raster(
        os.path.join(
            DATA_DIR,
            "population",
            "population_2020.tif"
        )
    )

    population = align_to_ref(
        population,
        pop_profile,
        ref_profile
    )

    population = normalize(
        clean_generic(population)
    )



    # STATIC LANDCOVER


    landcover, lc_profile = load_raster(
        os.path.join(
            DATA_DIR,
            "landcover",
            "landcover_2024.tif"
        )
    )

    landcover = align_to_ref(
        landcover,
        lc_profile,
        ref_profile,
        method="nearest"
    )

    landcover = clean_generic(landcover)

    # RGB → single feature
    if landcover.ndim == 3:
        landcover = np.mean(
            landcover,
            axis=2
        )

    landcover = normalize(landcover)



    # LIVE TEMPERATURE


    live_temp = fetch_live_temperature()

    temperature = create_temperature_raster(
        live_temp,
        ndvi.shape
    )

    temperature = clean_generic(temperature)

    # Approximate historical scaling
    temperature = temperature / 40.0


    #DEBUGGING
    print("\nLIVE FEATURE MEANS")


    print(f"NDVI mean: {ndvi.mean():.3f}")
    print(f"POP mean: {population.mean():.3f}")
    print(f"TEMP mean: {temperature.mean():.3f}")
    print(f"ELEV mean: {elevation.mean():.3f}")
    print(f"WATER mean: {water.mean():.3f}")
    print(f"LC mean: {landcover.mean():.3f}")   


    # FINAL FEATURE STACK


    X_live = np.stack([

        ndvi,          # Feature 0
        population,    # Feature 1
        temperature,   # Feature 2
        elevation,     # Feature 3
        water,         # Feature 4
        landcover      # Feature 5

    ], axis=-1)

    print("\nLIVE FEATURE STACK")


    print(f"Shape: {X_live.shape}")

    print("\nFeature ranges:")

    print(f"NDVI: {X_live[...,0].min():.3f} → {X_live[...,0].max():.3f}")

    print(f"POP:  {X_live[...,1].min():.3f} → {X_live[...,1].max():.3f}")

    print(f"TEMP: {X_live[...,2].min():.3f} → {X_live[...,2].max():.3f}")

    print(f"ELEV: {X_live[...,3].min():.3f} → {X_live[...,3].max():.3f}")

    print(f"WATER:{X_live[...,4].min():.3f} → {X_live[...,4].max():.3f}")

    print(f"LC:   {X_live[...,5].min():.3f} → {X_live[...,5].max():.3f}")


    return X_live, ref_profile



# TEST


if __name__ == "__main__":

    X_live, profile = load_live_data()

    print("\nSUCCESS")