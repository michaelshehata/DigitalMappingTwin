import json

from rasterio.features import shapes

from shapely.geometry import shape

def raster_to_geojson(binary_map):

    features = []

    for geom, value in shapes(
        binary_map.astype("uint8")
    ):

        if value == 1:

            features.append({

                "type": "Feature",

                "geometry": geom,

                "properties": {
                    "prediction": 1
                }
            })

    return {
        "type": "FeatureCollection",
        "features": features
    }