import "./Analysis.css";

function Analysis() {

  return (
    <div className="page-wrapper">

      <div className="page-content">

        <div className="content-card">

          <h1 className="page-title">
            Model Analysis
          </h1>

          <div className="analysis-grid">

            <div className="analysis-card">
              <h2>Prediction Accuracy</h2>
              <p>84%</p>
            </div>

            <div className="analysis-card">
              <h2>Urban Classification F1</h2>
              <p>0.81</p>
            </div>

            <div className="analysis-card">
              <h2>Vegetation Classification F1</h2>
              <p>0.79</p>
            </div>

            <div className="analysis-card">
              <h2>Model Type</h2>
              <p>Random Forest Classifier</p>
            </div>

          </div>

        </div>

      </div>

    </div>
  );
}

export default Analysis;