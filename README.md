# Digital Twin — Land Use Forecasting

A digital twin for forecasting and visualising land use change around Norwich, UK. The pipeline turns satellite and GIS rasters (RGB, NDVI, temperature, elevation, population, water distance, and land cover labels) into decadal land use forecasts up until 2124, shown in an interactive React web app.

**Author:** Michael Shehata 
**Supervisor:** Dr. Mohsin Raza 

---

## Prerequisites

- Python 3.11+
- Node.js 20+ (for the frontend)

---

## Setup

From the project root:

```bash (to create virtual environment for python dependencies)
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt

```


``` Data directory for raw data should look like:
data/ 
  elevation/elevation.tif
  rgb_landsat/rgb_{1985,1995,2005,2015,2024}.tif
  ndvi/ndvi_{1985,1995,2005,2015,2024}.tif
  temperature/temperature_{1985,1995,2005,2015,2024}.tif
  population/population_{2000,2010,2020}.tif
  water/distance_to_water.tif
  lcm/lcm1990_25m_gb.tif, lcm2007_25m_gb.tif, lcm2015_25m_gb.tif, lcm2023_25m_gb.tif
```

---

## Pipeline (preprocessing → prediction)

Run all commands from the project root with the virtual environment active.

### 1. Inspect and preprocess feature rasters

Reprojects, cleans, and normalises all `.tif` files under `data/` to a common grid in `processed_data/`:

```bash

python -m scripts.inspect_raw_data
python -m scripts.preprocess_data
python -m scripts.inspect_preprocessed_data
 
```

### 2. Preprocess land cover labels

Builds aligned label rasters (`labels_*.tif`) in `processed_data/` (requires `processed_data/elevation.tif` from step 1):

```bash
python -m scripts.preprocess_lcm_labels.py
```


### 3. Train models

**Production model** (Random Forest saved to `best_model/` — used by prediction):

```bash
python -m model.best_model.py
```

**Optional — compare Random Forest vs XGBoost** (metrics in `model_results/`):

```bash
python -m model.train_models.py
```

### 4. Generate forecasts

Projects features forward and writes GeoTIFFs and PNGs to `forecasts/`:

```bash
python -m model.predict_le.py
```

Requires `best_model/rf3_final_model.pkl` and `best_model/rf3_final_scaler.pkl` from step 3.

---

## Run the web app

Copy forecast images into the frontend public folder so the Visualization page can load them:

```bash
# Windows (PowerShell)
Copy-Item -Path forecasts\forecast_*.png -Destination frontend\public\forecasts\ -Force

Then start the dev server:

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173]


## Outputs

| Step | Output |
|------|--------|
| Preprocessing | `processed_data/*.tif` |
| Training | `best_model/`, `model_results/` |
| Prediction | `forecasts/forecast_<year>.tif`, `.png`, timeline and change maps |
