import rasterio

from rasterio.features import shapes
import geopandas as gpd

print("Converting raster to GeoJSON...")

with rasterio.open("outputs/predicted_map.tif") as src:
    image = src.read(1)

    mask = image == 1

    results = (
        {
            "properties": {"prediction": 1},
            "geometry": s
        }
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

gdf.to_file(
    "outputs/predicted_map.geojson",
    driver="GeoJSON"
)

print("GeoJSON exported successfully")