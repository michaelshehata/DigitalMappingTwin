import { useState } from "react";

import GlobeView from "../components/GlobeView";
import AnalyticsPanel from "../components/AnalyticsPanel";

import "./Visualization.css";

function Visualization() {
  const [populationGrowth, setPopulationGrowth] = useState(35);
  const [urbanExpansion, setUrbanExpansion] = useState(45);
  const [climateSeverity, setClimateSeverity] = useState(2);
  const [year, setYear] = useState(2035);

  return (
    <div className="visualization-page">
      <div className="visualization-layout">

        {/* LEFT PANEL */}
        <div className="controls-panel">
          <h2>Scenario Controls</h2>

          <div className="slider-group">
            <label>
              Population Growth: {populationGrowth}%
            </label>

            <input
              type="range"
              min="0"
              max="100"
              value={populationGrowth}
              onChange={(e) =>
                setPopulationGrowth(Number(e.target.value))
              }
            />
          </div>

          <div className="slider-group">
            <label>
              Urban Expansion: {urbanExpansion}%
            </label>

            <input
              type="range"
              min="0"
              max="100"
              value={urbanExpansion}
              onChange={(e) =>
                setUrbanExpansion(Number(e.target.value))
              }
            />
          </div>

          <div className="slider-group">
            <label>
              Temperature Increase: {climateSeverity}°C
            </label>

            <input
              type="range"
              min="0"
              max="5"
              step="0.1"
              value={climateSeverity}
              onChange={(e) =>
                setClimateSeverity(Number(e.target.value))
              }
            />
          </div>

          <div className="slider-group">
            <label>
              Simulation Year: {year}
            </label>

            <input
              type="range"
              min="2025"
              max="2050"
              value={year}
              onChange={(e) =>
                setYear(Number(e.target.value))
              }
            />
          </div>

          <button className="run-button">
            Run Simulation
          </button>
        </div>

        {/* CENTER GLOBE */}
        <div className="globe-panel">
          <GlobeView />
        </div>

        {/* RIGHT ANALYTICS */}
        <AnalyticsPanel
          populationGrowth={populationGrowth}
          urbanExpansion={urbanExpansion}
          climateSeverity={climateSeverity}
          year={year}
        />
      </div>
    </div>
  );
}

export default Visualization;