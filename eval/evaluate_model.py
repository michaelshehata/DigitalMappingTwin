import numpy as np
import joblib
from sklearn.metrics import classification_report, f1_score

from scripts.load_data import load_all_data

model = joblib.load("model_output/random_forest.pkl")

X, y, _ = load_all_data()

X_flat = X.reshape(-1, X.shape[-1])
y_flat = y.flatten()

chunk_size = 100000
preds = []

print("Evaluating in chunks:")

for i in range(0, len(X_flat), chunk_size):
    chunk = X_flat[i:i + chunk_size]

    prob = model.predict_proba(chunk)[:, 1]
    pred = (prob > 0.3).astype(int)

    preds.append(pred)

preds = np.concatenate(preds)

print("\nClassification Report:")
print(classification_report(y_flat, preds))
print("F1 Score:", f1_score(y_flat, preds))