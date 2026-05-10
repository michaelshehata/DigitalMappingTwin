import "./AnalyticsPanel.css";

function AnalyticsPanel() {
  return (
    <div className="analytics-panel">

      <h2>Simulation Analytics</h2>

      <div className="analytics-card">
        <h3>Urban Growth</h3>
        <p>14%</p>
      </div>

      <div className="analytics-card">
        <h3>Vegetation Loss</h3>
        <p>6%</p>
      </div>

      <div className="analytics-card">
        <h3>Flood Risk Increase</h3>
        <p>9%</p>
      </div>

    </div>
  );
}

export default AnalyticsPanel;