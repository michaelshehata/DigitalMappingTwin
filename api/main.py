# API ENTRY POINT

from fastapi import FastAPI
import joblib
import numpy as np

from scripts.load_data import load_all_data
from api.weather_api import get_live_weather
from api.rasterize_live import inject_live_data

app = FastAPI()

model = joblib.load("model_output/random_forest.pkl")


@app.get("/")
def root():
    return {"message": "Digital Twin API running"}


@app.get("/predict_live")
def predict_live():

    X, y, _ = load_all_data()

    # Get live weather
    weather = get_live_weather()

    # Inject into dataset
    X_live = inject_live_data(X, weather)

    # Flatten
    X_flat = X_live.reshape(-1, X_live.shape[-1])

    # Chunk prediction
    preds = []
    for i in range(0, len(X_flat), 100000):
        chunk = X_flat[i:i+100000]
        prob = model.predict_proba(chunk)[:, 1]
        preds.append((prob > 0.3).astype(int))

    preds = np.concatenate(preds)

    return {
        "status": "success",
        "temperature": weather["temperature"],
        "predicted_change_pixels": int(preds.sum())
    }