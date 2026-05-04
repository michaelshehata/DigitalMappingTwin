import numpy as np
import joblib
import os

from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

from xgboost import XGBClassifier

import sys
sys.path.append(os.path.abspath(".."))

from scripts.load_data import load_all_data


# LOAD DATA


X, y, _ = load_all_data()

X_flat = X.reshape(-1, X.shape[-1])
y_flat = y.flatten()

mask = (y_flat >= 0)
X_flat = X_flat[mask]
y_flat = y_flat[mask]

print("Dataset:", X_flat.shape)



# SAMPLE

sample_size = 200000
indices = np.random.choice(len(X_flat), sample_size, replace=False)

X_sample = X_flat[indices]
y_sample = y_flat[indices]

print("Sampled:", X_sample.shape)



# SPLIT (70 / 20 / 10)

# Step 1: 70% train, 30% temp
X_train, X_temp, y_train, y_temp = train_test_split(
    X_sample, y_sample, test_size=0.3, random_state=42
)

# Step 2: split temp → 20% test, 10% val
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=2/3, random_state=42
)

print("Train:", X_train.shape)
print("Validation:", X_val.shape)
print("Test:", X_test.shape)



# MODELS

models = {
    "random_forest": RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        n_jobs=-1,
        random_state=42,
        class_weight={0:1, 1:2}
    ),

    "gradient_boosting": HistGradientBoostingClassifier(
        max_iter=150,
        max_depth=10,
        learning_rate=0.1
    ),

    "logistic_regression": LogisticRegression(
        max_iter=200,
        class_weight="balanced"
    ),

    "xgboost": XGBClassifier(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        n_jobs=-1
    )
}



# TRAIN + EVALUATE + SAVE


os.makedirs("model_output", exist_ok=True)

results = {}

for name, model in models.items():
    print(f"\n===============================")
    print(f"Training: {name}")
    print("===============================")

    model.fit(X_train, y_train)

    # VALIDATION
    y_val_pred = model.predict(X_val)
    val_acc = accuracy_score(y_val, y_val_pred)

    print("\nValidation Accuracy:", val_acc)
    print(classification_report(y_val, y_val_pred))

    # TEST
    y_test_pred = model.predict(X_test)
    test_acc = accuracy_score(y_test, y_test_pred)

    print("\nTest Accuracy:", test_acc)
    print(classification_report(y_test, y_test_pred))

    # SAVE
    path = f"model_output/{name}.pkl"
    joblib.dump(model, path)

    print(f"\nSaved: {path}")

    results[name] = test_acc



# BEST MODEL

best_model = max(results, key=results.get)
print("\nBest model:", best_model, "Accuracy:", results[best_model])