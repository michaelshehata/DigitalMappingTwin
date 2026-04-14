import rasterio
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib


# LOAD DATA

with rasterio.open("data/norwich_cover/norwich_2020.tif") as src:
    land2020 = src.read(1)

with rasterio.open("data/norwich_cover/norwich_2021.tif") as src:
    land2021 = src.read(1)

print("Data loaded:", land2020.shape)



# FEATURE ENGINEERING (3x3 spatial window)

def create_features(image):
    features = []

    for i in range(1, image.shape[0] - 1):
        for j in range(1, image.shape[1] - 1):
            patch = image[i-1:i+2, j-1:j+2].flatten()
            features.append(patch)

    return np.array(features)


X = create_features(land2020)
y = land2021[1:-1, 1:-1].flatten()



# CLEAN DATA

mask = (X[:, 4] > 0) & (y > 0)

X = X[mask]
y = y[mask]

print("Final dataset size:", X.shape)

# TRAIN / TEST SPLIT

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)



# RANDOM FOREST

rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    n_jobs=-1,
    random_state=42
)

rf_model.fit(X_train, y_train)

rf_pred = rf_model.predict(X_test)

print("\n=== Random Forest Results ===")
print("Accuracy:", accuracy_score(y_test, rf_pred))
print(classification_report(y_test, rf_pred))



# DECISION TREE 

dt_model = DecisionTreeClassifier(random_state=42)

dt_model.fit(X_train, y_train)

dt_pred = dt_model.predict(X_test)

print("\n=== Decision Tree Results ===")
print("Accuracy:", accuracy_score(y_test, dt_pred))
print(classification_report(y_test, dt_pred))



# SAVE BEST MODEL 

joblib.dump(rf_model, "model/land_model.pkl")

print("\nModel saved as model/land_model.pkl")



# BASIC LAND ANALYSIS (for report)

print("\n=== Land Distribution (2020) ===")
unique, counts = np.unique(land2020, return_counts=True)
for u, c in zip(unique, counts):
    print(f"Class {u}: {c}")

print("\n=== Land Distribution (2021) ===")
unique, counts = np.unique(land2021, return_counts=True)
for u, c in zip(unique, counts):
    print(f"Class {u}: {c}")