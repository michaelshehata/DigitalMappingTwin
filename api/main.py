from fastapi import FastAPI
import joblib
import rasterio
import numpy as np
import osmnx as ox

app = FastAPI()

model = joblib.load("model/land_model.pkl")


def predict_map(model, image):
    output = image.copy()

    for i in range(1, image.shape[0] - 1):
        for j in range(1, image.shape[1] - 1):
            patch = image[i-1:i+2, j-1:j+2].flatten().reshape(1, -1)
            pred = model.predict(patch)[0]
            output[i, j] = pred

    return output


@app.get("/")
def root():
    return {"message": "Digital Twin API running"}


@app.get("/predict")
def predict():
    with rasterio.open("data/norwich_cover/norwich_2021.tif") as src:
        image = src.read(1)

    result = predict_map(model, image)

    return {
        "status": "prediction complete",
        "shape": result.shape
    }


@app.get("/simulate")
def simulate(steps: int = 2):
    with rasterio.open("data/norwich_cover/norwich_2021.tif") as src:
        current = src.read(1)

    for _ in range(steps):
        current = predict_map(model, current)

    return {
        "status": "simulation complete",
        "steps": steps
    }


@app.get("/osm")
def get_osm():
    gdf = ox.geometries_from_place("Norwich, UK", tags={"building": True})
    return {
        "status": "osm data fetched",
        "features": len(gdf)
    }


@app.get("/health")
def health():
    return {"status": "ok"}