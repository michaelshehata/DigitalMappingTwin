import { useState } from "react";

import GlobeView from "../components/GlobeView";

import "./Visualization.css";

function Visualization() {

  const [urbanExpansion, setUrbanExpansion] =
    useState(50);

  const [temperatureIncrease, setTemperatureIncrease] =
    useState(2);

  const [populationGrowth, setPopulationGrowth] =
    useState(35);

  const [simulationYear, setSimulationYear] =
    useState(2050);

  const [showPredictions, setShowPredictions] =
    useState(true);

  // DYNAMIC ANALYTICS
  const vegetationLoss =
    Math.round(urbanExpansion * 0.65);

  const floodRisk =
    Math.round(temperatureIncrease * 14);

  const urbanGrowth =
    urbanExpansion;

  return (
    <div className="visualization-page">

      <div className="visualization-layout">

        {/* LEFT PANEL */}

        <div className="controls-panel">

          <h2>
            Simulation Controls
          </h2>

          <div className="slider-group">
            <label>
              Urban Expansion:
              {urbanExpansion}%
            </label>

            <input
              type="range"
              min="0"
              max="100"
              value={urbanExpansion}
              onChange={(e) =>
                setUrbanExpansion(
                  Number(e.target.value)
                )
              }
            />
          </div>

          <div className="slider-group">
            <label>
              Temperature Increase:
              {temperatureIncrease}°C
            </label>

            <input
              type="range"
              min="0"
              max="6"
              step="0.1"
              value={temperatureIncrease}
              onChange={(e) =>
                setTemperatureIncrease(
                  Number(e.target.value)
                )
              }
            />
          </div>

          <div className="slider-group">
            <label>
              Population Growth:
              {populationGrowth}%
            </label>

            <input
              type="range"
              min="0"
              max="100"
              value={populationGrowth}
              onChange={(e) =>
                setPopulationGrowth(
                  Number(e.target.value)
                )
              }
            />
          </div>

          <div className="slider-group">
            <label>
              Simulation Year:
              {simulationYear}
            </label>

            <input
              type="range"
              min="2025"
              max="2125"
              value={simulationYear}
              onChange={(e) =>
                setSimulationYear(
                  Number(e.target.value)
                )
              }
            />
          </div>

          <div className="slider-group">

            <label>

              <input
                type="checkbox"
                checked={showPredictions}
                onChange={(e) =>
                  setShowPredictions(
                    e.target.checked
                  )
                }
              />

              {" "}
              Show Prediction Layer

            </label>

          </div>

          <button className="run-button">
            Run Simulation
          </button>

        </div>

        {/* CENTER PANEL */}

        <div className="globe-panel">

          <GlobeView
            showPredictions={
              showPredictions
            }
          />

        </div>

        {/* RIGHT PANEL */}

        <div className="analytics-panel">

          <h2>
            Simulation Analytics
          </h2>

          <div className="stat-card">
            <h3>
              Urban Growth
            </h3>

            <p>
              {urbanGrowth}% predicted
              expansion
            </p>
          </div>

          <div className="stat-card">
            <h3>
              Flood Risk
            </h3>

            <p>
              {floodRisk}% estimated
              flood vulnerability
            </p>
          </div>

          <div className="stat-card">
            <h3>
              Vegetation Loss
            </h3>

            <p>
              {vegetationLoss}% potential
              reduction
            </p>
          </div>

          <div className="stat-card">
            <h3>
              Simulation Year
            </h3>

            <p>
              Forecast model for
              {simulationYear}
            </p>
          </div>

        </div>

      </div>

    </div>
  );
}

export default Visualization;