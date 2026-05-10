import "./StatsGrid.css";

function StatsGrid() {
  return (
    <div className="stats-grid">

      <div className="stat-card">
        <h3>Urban Growth</h3>
        <p>+14%</p>
      </div>

      <div className="stat-card">
        <h3>Forest Loss</h3>
        <p>-6%</p>
      </div>

      <div className="stat-card">
        <h3>Population Increase</h3>
        <p>+22%</p>
      </div>

    </div>
  );
}

export default StatsGrid;