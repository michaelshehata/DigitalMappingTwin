import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import joblib

from scripts.load_data import load_all_data

model = joblib.load("model_output/random_forest.pkl")

X, y, _ = load_all_data()

X_flat = X.reshape(-1, X.shape[-1])
y_flat = y.flatten()

chunk_size = 100000
preds = []

for i in range(0, len(X_flat), chunk_size):
    chunk = X_flat[i:i + chunk_size]
    prob = model.predict_proba(chunk)[:, 1]
    pred = (prob > 0.3).astype(int)
    preds.append(pred)

preds = np.concatenate(preds)

cm = confusion_matrix(y_flat, preds)

plt.imshow(cm)
plt.title("Confusion Matrix")
plt.colorbar()

plt.xlabel("Predicted")
plt.ylabel("Actual")

for i in range(2):
    for j in range(2):
        plt.text(j, i, cm[i, j], ha="center", va="center")

plt.show()