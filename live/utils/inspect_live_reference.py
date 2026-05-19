import rasterio

path = "data/ndvi/ndvi_2024.tif"

with rasterio.open(path) as src:

    print("\nRASTER INFO")
    print("=" * 50)

    print("CRS:")
    print(src.crs)

    print("\nWidth:")
    print(src.width)

    print("\nHeight:")
    print(src.height)

    print("\nBounds:")
    print(src.bounds)

    print("\nResolution:")
    print(src.res)

    print("\nTransform:")
    print(src.transform)

    print("=" * 50)