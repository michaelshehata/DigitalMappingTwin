from rasterio.features import shapes
import rasterio
import geopandas as gpd

print("Converting raster to simplified GeoJSON...")

with rasterio.open("outputs/predicted_map.tif") as src:
    image = src.read(1)

    mask = image == 1

    results = (
        {"properties": {"prediction": 1}, "geometry": s}
        for s, v in shapes(
            image,
            mask=mask,
            transform=src.transform
        )
    )

    geoms = list(results)

    gdf = gpd.GeoDataFrame.from_features(
        geoms,
        crs=src.crs
    )

# HUGE PERFORMANCE BOOST
gdf["geometry"] = gdf.geometry.simplify(
    tolerance=0.0005,
    preserve_topology=True
)

# REMOVE INVALID GEOMETRIES
gdf = gdf[gdf.is_valid]

# SAVE
gdf.to_file(
    "frontend/public/data/predicted_map.geojson",
    driver="GeoJSON"
)

print("Simplified GeoJSON saved.")