import numpy as np
import matplotlib.pyplot as plt
import rasterio
import joblib

from scripts.load_data import load_all_data

model = joblib.load("model_output/random_forest.pkl")

X, y, _ = load_all_data()

X_flat = X.reshape(-1, X.shape[-1])

chunk_size = 100000
preds = []

for i in range(0, len(X_flat), chunk_size):
    chunk = X_flat[i:i + chunk_size]
    prob = model.predict_proba(chunk)[:, 1]
    pred = (prob > 0.3).astype(int)
    preds.append(pred)

preds = np.concatenate(preds)

pred_map = preds.reshape(y.shape)

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.title("Actual Change")
plt.imshow(y, cmap="Reds")

plt.subplot(1, 2, 2)
plt.title("Predicted Change")
plt.imshow(pred_map, cmap="Reds")

plt.show()