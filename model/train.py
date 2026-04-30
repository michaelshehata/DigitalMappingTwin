import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

import sys
import os
sys.path.append(os.path.abspath(".."))

from scripts.load_data import load_all_data


# LOAD DATA

X, y, _ = load_all_data()

# Flatten
X_flat = X.reshape(-1, X.shape[-1])
y_flat = y.flatten()

print("Dataset:", X_flat.shape)

# Remove invalid pixels

mask = (y_flat >= 0)
X_flat = X_flat[mask]
y_flat = y_flat[mask]

# SAMPLE SIZE

sample_size = 100000  

indices = np.random.choice(len(X_flat), sample_size, replace=False)

X_sample = X_flat[indices]
y_sample = y_flat[indices]

print("Sampled dataset:", X_sample.shape)


# ===============================
# SPLIT: 70 / 20 / 10
# ===============================

# First split: 70 train, 30 temp
X_train, X_temp, y_train, y_temp = train_test_split(
    X_sample, y_sample, test_size=0.3, random_state=42
)

# Second split: 20 test, 10 val (from the 30%)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=2/3, random_state=42
)

print("Train:", X_train.shape)
print("Validation:", X_val.shape)
print("Test:", X_test.shape)



# MODEL


model = RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    n_jobs=-1,
    random_state=42,
    verbose=1,
    class_weight={0:1, 1:2}
)

print("\nTraining model...")
model.fit(X_train, y_train)
print("Training complete")



# VALIDATION

y_val_pred = model.predict(X_val)

print("\nValidation Accuracy:", accuracy_score(y_val, y_val_pred))
print("\nValidation Report:\n", classification_report(y_val, y_val_pred))



# TEST

y_test_pred = model.predict(X_test)

print("\nTest Accuracy:", accuracy_score(y_test, y_test_pred))
print("\nTest Report:\n", classification_report(y_test, y_test_pred))



# SAVE MODEL


os.makedirs("model", exist_ok=True)

joblib.dump(model, "model/land_model.pkl")

print("\nModel saved")