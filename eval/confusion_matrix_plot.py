import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import joblib

from scripts.load_data import load_all_data

# Load model + data
model = joblib.load("model/land_model.pkl")
X, y, _ = load_all_data()

# Flatten
X_flat = X.reshape(-1, X.shape[-1])
y_flat = y.flatten()

# Predict
y_pred = model.predict(X_flat)

# Confusion matrix
cm = confusion_matrix(y_flat, y_pred)

# Plot
plt.imshow(cm)
plt.title("Confusion Matrix")
plt.colorbar()

plt.xlabel("Predicted")
plt.ylabel("Actual")

for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        plt.text(j, i, cm[i, j], ha="center", va="center")

plt.show()