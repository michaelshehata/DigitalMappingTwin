import "./Analysis.css";

function Analysis() {
  return (
    <div className="page-wrapper">
      <div className="page-content">
        
        {/* Core Performance Section */}
        <div className="content-card">
          <h1 className="page-title">Model Performance Analysis</h1>

          <div className="analysis-grid">
            <div className="analysis-card">
              <h2>Overall Prediction Accuracy</h2>
              <p>68.79%</p>
            </div>

            <div className="analysis-card">
              <h2>Macro-Averaged F1 Score</h2>
              <p>0.4617</p>
            </div>

            <div className="analysis-card">
              <h2>Cohen's Kappa (κ)</h2>
              <p>0.4830</p>
            </div>

            <div className="analysis-card">
              <h2>Urban Classification Rate</h2>
              <p>~78.0%</p>
            </div>

            <div className="analysis-card">
              <h2>Vegetation Classification Rate</h2>
              <p>52.3%</p>
            </div>

          </div>
        </div>

        {/* Winning Model Hyperparameters Section */}
        <div className="content-card" style={{ marginTop: "30px" }}>
          <h1 className="page-title">Winning Model Hyperparameters</h1>

          <div className="analysis-grid">
            <div className="analysis-card">
              <h2>Number of Estimators</h2>
              <p>300</p>
            </div>

            <div className="analysis-card">
              <h2>Maximum Tree Depth</h2>
              <p>None</p>
            </div>

            <div className="analysis-card">
              <h2>Min Samples Split</h2>
              <p>10</p>
            </div>

            <div className="analysis-card">
              <h2>Class Weights</h2>
              <p>'balanced'</p>
            </div>

            <div className="analysis-card">
              <h2>Random Seed State</h2>
              <p>6001</p>
            </div>

            <div className="analysis-card">
              <h2>Splitting Criterion</h2>
              <p>Gini Impurity</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

export default Analysis;