import joblib
import matplotlib.pyplot as plt

# Load model
model = joblib.load("model/land_model.pkl")

# Feature names
features = ["NDVI", "Elevation", "Population", "Temperature", "Water"]

# Importance
importances = model.feature_importances_

# Plot
plt.figure()
plt.bar(features, importances)
plt.title("Feature Importance")
plt.xlabel("Features")
plt.ylabel("Importance")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()