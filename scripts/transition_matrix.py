import rasterio
import numpy as np

# Load data
with rasterio.open("data/norwich_cover/norwich_2020.tif") as src:
    land2020 = src.read(1)

with rasterio.open("data/norwich_cover/norwich_2021.tif") as src:
    land2021 = src.read(1)

# Flatten
a = land2020.flatten()
b = land2021.flatten()

# Mask invalid values
mask = (a > 0) & (b > 0)

a = a[mask]
b = b[mask]

# Build transition matrix
matrix = {}

for i, j in zip(a, b):
    key = (int(i), int(j))
    matrix[key] = matrix.get(key, 0) + 1

# Print results
print("Transition Matrix (from → to):")
for k, v in matrix.items():
    print(f"{k[0]} → {k[1]}: {v}")