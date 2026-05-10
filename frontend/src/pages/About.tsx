import "./About.css";

function About() {
  return (
    <div className="page-wrapper">

      <div className="page-content">

        <div className="content-card">

          <h1 className="page-title">
            About The Project
          </h1>

          <p className="page-text">
            This project explores Digital Twin technology
            for long-term land use simulation in Norwich
            using GIS, satellite imagery, environmental
            data, and machine learning models.
          </p>

          <p className="page-text">
            The platform visualizes future urban growth,
            environmental change, and land use patterns
            over a 100-year period through interactive
            geospatial simulation.
          </p>

        </div>

      </div>

    </div>
  );
}

export default About;