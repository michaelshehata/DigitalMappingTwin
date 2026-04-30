import numpy as np
from sklearn.metrics import accuracy_score, classification_report
import joblib

from scripts.load_data import load_all_data

# Load model
model = joblib.load("model/land_model.pkl")

# Load data
X, y, _ = load_all_data()

# Flatten
X_flat = X.reshape(-1, X.shape[-1])
y_flat = y.flatten()

# Predict
y_pred = model.predict(X_flat)

# Metrics
print("Accuracy:", accuracy_score(y_flat, y_pred))
print("\nClassification Report:\n", classification_report(y_flat, y_pred))