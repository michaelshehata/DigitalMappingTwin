import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

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



# TRAIN / TEST SPLIT

X_train, X_test, y_train, y_test = train_test_split(
    X_flat, y_flat, test_size=0.25, random_state=42
)



# MODEL

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=20,
    n_jobs=-1,
    random_state=42
)

model.fit(X_train, y_train)



# EVALUATE

y_pred = model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))



# SAVE

joblib.dump(model, "model/land_model.pkl")
print("\nModel saved")