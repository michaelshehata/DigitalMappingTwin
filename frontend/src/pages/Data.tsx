import "./Data.css";

const dataSources = [
  {
    title: "Landcover",
    image:
      "https://developers.google.com/earth-engine/datasets/images/GOOGLE/GOOGLE_DYNAMICWORLD_V1_sample.png",

    description:
      "Dynamic World is a 10m land cover dataset that includes class probabilities and label information for nine classes.",

    link:
      "https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1"
  },

  {
    title: "Temperature",
    image:
      "https://developers.google.com/earth-engine/datasets/images/ECMWF/ECMWF_ERA5_LAND_MONTHLY_AGGR_sample.png",

    description:
      "ERA5-Land is a reanalysis dataset providing a consistent view of the evolution of land variables over several decades at an enhanced resolution.",

    link:
      "https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_MONTHLY_AGGR"
  },

  {
    title: "Population Data",
    image:
      "https://developers.google.com/earth-engine/datasets/images/WorldPop/WorldPop_GP_100m_pop_sample.png",

    description:
      "add.",

    link:
      "https://developers.google.com/earth-engine/datasets/catalog/WorldPop_GP_100m_pop"
  },

  {
    title: "Vegetation",
    image:
      "https://developers.google.com/earth-engine/datasets/images/COPERNICUS/COPERNICUS_S2_SR_HARMONIZED_sample.png",

    description:
      "Land cover classification maps for environmental and urban planning analysis.",

    link:
      "https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED"
  },

  {
    title: "Elevation",
    image:
      "https://developers.google.com/earth-engine/datasets/images/USGS/USGS_SRTMGL1_003_sample.png",

    description:
      "Global digital elevation model produced from NASA’s SRTM. It provides near global elevation data at 30m resolution.",

    link:
      "https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003"
  },

  {
    title: "Water Proximity",
    image:
      "https://developers.google.com/earth-engine/datasets/images/JRC/JRC_GSW1_4_GlobalSurfaceWater_sample.png",

    description:
      "Global satellite-derived dataset that maps the location, extent, and seasonal changes of surface water using Landsat imagery.",

    link:
      "https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_GlobalSurfaceWater"
  }
];

export default function Data() {
  return (
    <div className="page-wrapper">
      <div className="page-content">
        <div className="content-card">

          <h1 className="page-title">
            Data Sources
          </h1>

          <div className="data-grid">

            {dataSources.map((item) => (
              <div
                key={item.title}
                className="data-card"
              >
                <img
                  src={item.image}
                  alt={item.title}
                  className="data-image"
                />

                <div className="data-content">
                  <h2>{item.title}</h2>

                  <p>{item.description}</p>

                  <a
                    href={item.link}
                    target="_blank"
                    rel="noreferrer"
                    className="data-link"
                  >
                    Visit Source →
                  </a>
                </div>
              </div>
            ))}

          </div>
        </div>
      </div>
    </div>
  );
}