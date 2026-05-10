import "./AnalyticsPanel.css";

interface Props {
  populationGrowth: number;
  urbanExpansion: number;
  climateSeverity: number;
  year: number;
}

function AnalyticsPanel({
  populationGrowth,
  urbanExpansion,
  climateSeverity,
  year,
}: Props) {

  const vegetationLoss =
    Math.round((urbanExpansion * 0.4 + climateSeverity * 8));

  const floodRisk =
    Math.round((climateSeverity * 12 + urbanExpansion * 0.3));

  return (
    <div className="analytics-panel">
      <h2>Simulation Analytics</h2>

      <div className="stat-card">
        <h3>Urban Growth</h3>
        <p>{populationGrowth}%</p>
      </div>

      <div className="stat-card">
        <h3>Vegetation Loss</h3>
        <p>{vegetationLoss}%</p>
      </div>

      <div className="stat-card">
        <h3>Flood Risk Increase</h3>
        <p>{floodRisk}%</p>
      </div>

      <div className="stat-card">
        <h3>Prediction Year</h3>
        <p>{year}</p>
      </div>
    </div>
  );
}

export default AnalyticsPanel;