import "./Analysis.css";

function Analysis() {
  return (
    <div className="analysis-page">

      <h1>Model Analysis</h1>

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

      </div>

    </div>
  );
}

export default Analysis;