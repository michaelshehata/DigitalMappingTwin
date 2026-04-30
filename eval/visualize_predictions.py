import matplotlib.pyplot as plt
import joblib


from scripts.load_data import load_all_data

# Load model + data
model = joblib.load("model/land_model.pkl")
X, y, _ = load_all_data()

# Predict
X_flat = X.reshape(-1, X.shape[-1])
y_pred = model.predict(X_flat)

pred_map = y_pred.reshape(y.shape)

# Plot
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.imshow(y)
plt.title("Actual Change")

plt.subplot(1, 2, 2)
plt.imshow(pred_map)
plt.title("Predicted Change")

plt.show()