import "./ScenarioPanel.css";

function ScenarioPanel() {
  return (
    <div className="scenario-panel">

      <h2>Scenario Controls</h2>

      <div className="control-group">
        <label>Population Growth</label>
        <input type="range" min="0" max="100" />
      </div>

      <div className="control-group">
        <label>Urban Expansion</label>
        <input type="range" min="0" max="100" />
      </div>

      <div className="control-group">
        <label>Climate Severity</label>
        <input type="range" min="0" max="100" />
      </div>

      <div className="control-group">
        <label>Year</label>
        <input type="range" min="2025" max="2125" />
      </div>

      <button className="simulate-btn">
        Run Simulation
      </button>

    </div>
  );
}

export default ScenarioPanel;