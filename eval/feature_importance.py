import joblib
import matplotlib.pyplot as plt

model = joblib.load("model_output/random_forest.pkl")

features = ["NDVI", "Population", "Temperature", "Elevation", "Water"]

importances = model.feature_importances_

plt.figure()
plt.bar(features, importances)
plt.title("Feature Importance")
plt.ylabel("Importance")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()