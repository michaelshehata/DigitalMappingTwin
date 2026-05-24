import os
import pandas as pd
import matplotlib.pyplot as plt


# CONFIG


INPUT_CSV = "model_results/RF_3_feature_importance.csv"

OUTPUT_DIR = "figures"
OUTPUT_PATH = f"{OUTPUT_DIR}/rf_feature_importance.png"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# LOAD FEATURE IMPORTANCE


df = pd.read_csv(INPUT_CSV)


# ORIGINAL FEATURE ORDER
# Must match training pipeline exactly


original_features = [
    "Red",
    "Green",
    "Blue",
    "NDVI",
    "NDWI",
    "NDBI",
    "Temperature",
    "Population",
    "Elevation",
    "Distance to Water"
]

df["feature"] = original_features


# GROUP FEATURES INTO CONCEPT DATASETS


group_mapping = {
    "Red": "Spectral Reflectance",
    "Green": "Spectral Reflectance",
    "Blue": "Spectral Reflectance",

    "NDVI": "Spectral Indices",
    "NDWI": "Spectral Indices",
    "NDBI": "Spectral Indices",

    "Temperature": "Temperature",
    "Population": "Population",
    "Elevation": "Elevation",
    "Distance to Water": "Distance to Water"
}

df["group"] = df["feature"].map(group_mapping)


# SUM IMPORTANCE BY GROUP


grouped_df = (
    df.groupby("group")["importance"]
    .sum()
    .reset_index()
)


# SORT FOR CLEANER VISUALISATION


grouped_df = grouped_df.sort_values(
    by="importance",
    ascending=True
)


# PLOT


fig, ax = plt.subplots(figsize=(9, 6))

ax.barh(
    grouped_df["group"],
    grouped_df["importance"]
)

for i, value in enumerate(grouped_df["importance"]):
    ax.text(
        value + 0.005,
        i,
        f"{value:.3f}",
        va="center"
    )

ax.set_xlabel("Combined Feature Importance")
ax.set_ylabel("Environmental Dataset")

ax.set_title(
    "Random Forest Environmental Feature Importance"
)

plt.tight_layout()


# SAVE


plt.savefig(
    OUTPUT_PATH,
    dpi=300,
    bbox_inches="tight"
)

print(f"Saved figure to: {OUTPUT_PATH}")