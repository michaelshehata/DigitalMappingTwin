import numpy as np
import matplotlib.pyplot as plt
import joblib

from scripts.load_data import load_all_data

# Load model + data
model = joblib.load("model/land_model.pkl")
X, y, _ = load_all_data()


def run_scenario(X_mod, name):
    X_flat = X_mod.reshape(-1, X_mod.shape[-1])
    pred = model.predict(X_flat)
    return pred.reshape(y.shape)



# SCENARIOS


# Baseline
baseline = run_scenario(X, "Baseline")

# Urban growth (increase population)
X_growth = X.copy()
X_growth[..., 2] *= 1.5
growth = run_scenario(X_growth, "Growth")

# Conservation (increase vegetation)
X_conserve = X.copy()
X_conserve[..., 0] *= 1.2
conserve = run_scenario(X_conserve, "Conservation")



# VISUALISE

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