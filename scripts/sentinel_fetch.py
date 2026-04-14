from sentinelhub import SHConfig, SentinelHubRequest, DataCollection, MimeType, BBox, CRS

config = SHConfig()

bbox = BBox(bbox=[1.20, 52.55, 1.40, 52.70], crs=CRS.WGS84)

request = SentinelHubRequest(
    data_folder="data/sentinel",
    evalscript="""
    //VERSION=3
    function setup() {
        return {
            input: ["B04", "B03", "B02"],
            output: { bands: 3 }
        };
    }

    function evaluatePixel(sample) {
        return [sample.B04, sample.B03, sample.B02];
    }
    """,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=("2023-01-01", "2023-01-10"),
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=bbox,
    size=(512, 512),
    config=config,
)

data = request.get_data()

print("Downloaded Sentinel data")