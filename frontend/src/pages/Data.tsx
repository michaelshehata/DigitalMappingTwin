import "./Data.css";

function Data() {
  return (
    <div className="page-wrapper">

      <div className="page-content">

        <div className="content-card">

          <h1 className="page-title">
            Data Sources
          </h1>

          <div className="data-grid">

            <div className="data-card">
              <h2>Satellite Imagery</h2>
              <p>Sentinel-2 Multispectral Data</p>
            </div>

            <div className="data-card">
              <h2>GIS Layers</h2>
              <p>OpenStreetMap + Norwich Boundaries</p>
            </div>

            <div className="data-card">
              <h2>Population Data</h2>
              <p>UK Census & Demographic Statistics</p>
            </div>

            <div className="data-card">
              <h2>Land Cover</h2>
              <p>CORINE Environmental Dataset</p>
            </div>

          </div>

        </div>

      </div>

    </div>
  );
}

export default Data;