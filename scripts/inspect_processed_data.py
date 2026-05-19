import os
import rasterio

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(
    BASE_DIR,
    "processed_data"
)

reference_file = "elevation.tif"

reference_path = os.path.join(
    DATA_DIR,
    reference_file
)


with rasterio.open(reference_path) as ref:

    ref_crs = ref.crs
    ref_transform = ref.transform
    ref_width = ref.width
    ref_height = ref.height
    ref_bounds = ref.bounds
    ref_res = ref.res


print("REFERENCE RASTER")


print(f"File: {reference_file}")
print(f"CRS: {ref_crs}")
print(f"Transform: {ref_transform}")
print(f"Width: {ref_width}")
print(f"Height: {ref_height}")
print(f"Bounds: {ref_bounds}")
print(f"Resolution: {ref_res}")


print("VALIDATION RESULTS")


all_valid = True


for filename in os.listdir(DATA_DIR):

    if not filename.endswith(".tif"):
        continue

    filepath = os.path.join(
        DATA_DIR,
        filename
    )

    with rasterio.open(filepath) as src:

        issues = []

        if src.crs != ref_crs:
            issues.append("CRS mismatch")

        if src.transform != ref_transform:
            issues.append("Transform mismatch")

        if src.width != ref_width:
            issues.append("Width mismatch")

        if src.height != ref_height:
            issues.append("Height mismatch")

        if src.bounds != ref_bounds:
            issues.append("Bounds mismatch")

        if src.res != ref_res:
            issues.append("Resolution mismatch")

        if len(issues) == 0:

            print(f"\n{filename}")
            print("Status: VALID")

        else:

            all_valid = False

            print(f"\n{filename}")
            print("Status: INVALID")

            for issue in issues:
                print(f"- {issue}")




if all_valid:

    print("Valid")

else:

    print("Failed")

