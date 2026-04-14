import rasterio
import matplotlib.pyplot as plt

# Load 2020
with rasterio.open("data/norwich_cover/norwich_2020.tif") as src:
    land2020 = src.read(1)

# Load 2021
with rasterio.open("data/norwich_cover/norwich_2021.tif") as src:
    land2021 = src.read(1)

print("Shape:", land2020.shape)

# Show both
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.imshow(land2020)
plt.title("2020")

plt.subplot(1, 2, 2)
plt.imshow(land2021)
plt.title("2021")

plt.show()