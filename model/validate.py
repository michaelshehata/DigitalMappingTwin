from scripts.load_data import load_all_data
import numpy as np
from sklearn.metrics import accuracy_score
import joblib

model = joblib.load("model/land_model.pkl")

X, y, _ = load_all_data()

X_flat = X.reshape(-1, X.shape[-1])
y_flat = y.flatten()

pred = model.predict(X_flat)

print("Validation Accuracy:", accuracy_score(y_flat, pred))