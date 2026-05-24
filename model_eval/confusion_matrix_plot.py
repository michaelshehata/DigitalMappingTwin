import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# CONFIG


INPUT_CSV = "model_results/XGB_3_test_confusion_matrix.csv"

OUTPUT_DIR = "figures"
OUTPUT_PATH = f"{OUTPUT_DIR}/xgb_confusion_matrix.png"

CLASS_NAMES = [
    "Vegetation",
    "Agriculture",
    "Urban",
    "Water",
    "Sparse"
]

os.makedirs(OUTPUT_DIR, exist_ok=True)


# LOAD CONFUSION MATRIX


cm = pd.read_csv(INPUT_CSV).values


# NORMALISE ROWS


cm_normalised = cm.astype(float) / cm.sum(axis=1, keepdims=True)


# PLOT


fig, ax = plt.subplots(figsize=(8, 6))

im = ax.imshow(cm_normalised, vmin=0, vmax=1)

# Axis ticks
ax.set_xticks(np.arange(len(CLASS_NAMES)))
ax.set_yticks(np.arange(len(CLASS_NAMES)))

# Labels
ax.set_xticklabels(CLASS_NAMES, rotation=20, ha="right")
ax.set_yticklabels(CLASS_NAMES)

ax.set_xlabel("Predicted Land Cover Class")
ax.set_ylabel("True Land Cover Class")

ax.set_title("Normalised Confusion Matrix for XGBoost Test Predictions")


# CELL VALUES


for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):

        percentage = cm_normalised[i, j] * 100

        ax.text(
            j,
            i,
            f"{percentage:.1f}%",
            ha="center",
            va="center",
            fontsize=9
        )


# COLOUR BAR


cbar = fig.colorbar(im)
cbar.set_label("Classification Percentage")

plt.tight_layout()


# SAVE


plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches="tight")

print(f"Saved confusion matrix figure to: {OUTPUT_PATH}")