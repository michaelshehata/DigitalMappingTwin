import numpy as np
import joblib
import os

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score

from xgboost import XGBClassifier

import sys
sys.path.append(os.path.abspath(".."))

from scripts.load_data import load_all_data


X, y, _ = load_all_data()

X_flat = X.reshape(-1, X.shape[-1])
y_flat = y.flatten()

mask = (y_flat >= 0)
X_flat = X_flat[mask]
y_flat = y_flat[mask]

print("Dataset:", X_flat.shape)


# Class distribution
unique, counts = np.unique(y_flat, return_counts=True)
print("\nClass distribution:")
for u, c in zip(unique, counts):
    print(f"Class {u}: {c}")


# Sample
sample_size = 200000
indices = np.random.choice(len(X_flat), sample_size, replace=False)

X_sample = X_flat[indices]
y_sample = y_flat[indices]


# Split
X_train, X_temp, y_train, y_temp = train_test_split(
    X_sample, y_sample, test_size=0.3, stratify=y_sample, random_state=42
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=2/3, stratify=y_temp, random_state=42
)


# Imbalance handling
scale_pos_weight = len(y_train[y_train == 0]) / len(y_train[y_train == 1])


models = {
    "random_forest": RandomForestClassifier(
        n_estimators=150,
        max_depth=30,
        n_jobs=-1,
        random_state=42,
        class_weight={0:1, 1:5}
    ),

    "xgboost": XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        n_jobs=-1,
        scale_pos_weight=scale_pos_weight
    )
}


os.makedirs("model_output", exist_ok=True)

results = {}

for name, model in models.items():
    print(f"\nTraining: {name}")

    model.fit(X_train, y_train)

    # Probability threshold
    y_val_prob = model.predict_proba(X_val)[:, 1]
    y_val_pred = (y_val_prob > 0.3).astype(int)

    print("\nValidation:")
    print(classification_report(y_val, y_val_pred))

    y_test_prob = model.predict_proba(X_test)[:, 1]
    y_test_pred = (y_test_prob > 0.3).astype(int)

    print("\nTest:")
    print(classification_report(y_test, y_test_pred))

    joblib.dump(model, f"model_output/{name}.pkl")

    results[name] = f1_score(y_test, y_test_pred)


best = max(results, key=results.get)
print("\nBest model:", best)