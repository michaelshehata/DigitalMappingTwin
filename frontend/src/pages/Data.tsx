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
      "https://miro.medium.com/v2/resize:fit:1100/format:webp/1*j-cTRXVuaJT2tjJQk5fD6A.png",

    description:
      "Worldpop provides high-resolution global population estimates at 100 m resolution.",

    link:
      "https://developers.google.com/earth-engine/datasets/catalog/WorldPop_GP_100m_pop"
  },

  {
    title: "Vegetation",
    image:
      "https://www.esa.int/var/esa/storage/images/esa_multimedia/images/2020/05/southern_ukraine/21988511-1-eng-GB/Southern_Ukraine.jpg",

    description:
      "Sentinel-2 is a satellite mission that provides high-resolution optical imagery for land cover classification maps for environmental and urban planning analysis.",

    link:
      "https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED"
  },

  {
    title: "Elevation",
    image:
      "https://www.researchgate.net/publication/237707716/figure/fig2/AS:298948293087236@1448286235339/Digital-elevation-model-DTED2-of-the-study-area-Height-of-the-scale-bar-expressed-in.png",

    description:
      "SRTM is a global digital elevation model produced by NASA. It provides near global elevation data at 30m resolution.",

    link:
      "https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003"
  },

  {
    title: "Water Proximity",
    image:
      "https://developers.google.com/earth-engine/datasets/images/JRC/JRC_GSW1_4_GlobalSurfaceWater_sample.png",

    description:
      "JRC is a global satellite-derived dataset that maps the location, extent, and seasonal changes of surface water using Landsat imagery.",

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