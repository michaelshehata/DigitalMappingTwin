import osmnx as ox
import matplotlib.pyplot as plt

place = "Norwich, UK"

# Get buildings
buildings = ox.geometries_from_place(place, tags={"building": True})

# Plot
fig, ax = plt.subplots(figsize=(8, 8))
buildings.plot(ax=ax, color="black")

plt.title("OSM Buildings - Norwich")
plt.show()