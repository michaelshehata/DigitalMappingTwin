import numpy as np
import matplotlib.pyplot as plt
import joblib

from scripts.load_data import load_all_data

model = joblib.load("model_output/random_forest.pkl")

X, y, _ = load_all_data()


def run_scenario(X_mod):
    X_flat = X_mod.reshape(-1, X_mod.shape[-1])

    preds = []
    chunk_size = 100000

    for i in range(0, len(X_flat), chunk_size):
        chunk = X_flat[i:i + chunk_size]
        prob = model.predict_proba(chunk)[:, 1]
        pred = (prob > 0.3).astype(int)
        preds.append(pred)

    preds = np.concatenate(preds)

    return preds.reshape(y.shape)


baseline = run_scenario(X)

X_growth = X.copy()
X_growth[..., 1] *= 1.5   # population
growth = run_scenario(X_growth)

X_conserve = X.copy()
X_conserve[..., 0] *= 1.2  # NDVI
conserve = run_scenario(X_conserve)


plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.imshow(baseline)
plt.title("Baseline")

plt.subplot(1, 3, 2)
plt.imshow(growth)
plt.title("Urban Growth")

plt.subplot(1, 3, 3)
plt.imshow(conserve)
plt.title("Conservation")

plt.show()