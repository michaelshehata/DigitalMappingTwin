import { useState } from "react";
import axios from "axios";

import GlobeView from "../components/MapView";

import "./Visualization.css";

function Visualization() {

  const [threshold, setThreshold] =
    useState(0.35);

  const [steps, setSteps] =
    useState(10);

  const [showProbability, setShowProbability] =
    useState(true);

  const [showBinary, setShowBinary] =
    useState(true);

  const [showNDVI, setShowNDVI] =
    useState(false);

  const [loading, setLoading] =
    useState(false);

  const [analytics, setAnalytics] =
    useState<any>(null);

  const runSimulation = async () => {

    try {

      setLoading(true);

      const response = await axios.post(
        `http://127.0.0.1:8000/predict?threshold=${threshold}&steps=${steps}`
      );

      setAnalytics(response.data);

    } catch (error) {

      console.error(error);

    } finally {

      setLoading(false);

    }
  };

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
              Threshold: {threshold.toFixed(2)}
            </label>

            <input
              type="range"
              min="0.1"
              max="0.9"
              step="0.01"
              value={threshold}
              onChange={(e) =>
                setThreshold(
                  Number(e.target.value)
                )
              }
            />

          </div>

          <div className="slider-group">

            <label>
              Forecast Steps: {steps}
            </label>

            <input
              type="range"
              min="1"
              max="30"
              step="1"
              value={steps}
              onChange={(e) =>
                setSteps(
                  Number(e.target.value)
                )
              }
            />

          </div>

          <div className="prediction-toggle">

            <label className="prediction-switch">

              <input
                type="checkbox"
                checked={showProbability}
                onChange={(e) =>
                  setShowProbability(
                    e.target.checked
                  )
                }
              />

              <span className="slider"></span>

            </label>

            <p className="predictionText">
              Probability Layer
            </p>

          </div>

          <div className="prediction-toggle">

            <label className="prediction-switch">

              <input
                type="checkbox"
                checked={showBinary}
                onChange={(e) =>
                  setShowBinary(
                    e.target.checked
                  )
                }
              />

              <span className="slider"></span>

            </label>

            <p className="predictionText">
              Binary Prediction
            </p>

          </div>

          <div className="prediction-toggle">

            <label className="prediction-switch">

              <input
                type="checkbox"
                checked={showNDVI}
                onChange={(e) =>
                  setShowNDVI(
                    e.target.checked
                  )
                }
              />

              <span className="slider"></span>

            </label>

            <p className="predictionText">
              NDVI Layer
            </p>

          </div>

          <button
            className="run-button"
            onClick={runSimulation}
          >
            {
              loading
                ? "Running..."
                : "Run Simulation"
            }
          </button>

        </div>

        {/* CENTER PANEL */}

        <div className="globe-panel">

          <GlobeView
            showProbability={showProbability}
            showBinary={showBinary}
            showNDVI={showNDVI}
          />

        </div>

        {/* RIGHT PANEL */}

        <div className="analytics-panel">

          <h2>
            Simulation Analytics
          </h2>

          {
            analytics && (
              <>

                <div className="stat-card">
                  <h3>
                    Predicted Change
                  </h3>

                  <p>
                    {
                      analytics.predicted_change_percentage
                    }%
                  </p>
                </div>

                <div className="stat-card">
                  <h3>
                    Changed Pixels
                  </h3>

                  <p>
                    {
                      analytics.predicted_change_pixels
                    }
                  </p>
                </div>

                <div className="stat-card">
                  <h3>
                    Probability Mean
                  </h3>

                  <p>
                    {
                      analytics.probability_mean.toFixed(3)
                    }
                  </p>
                </div>

                <div className="stat-card">
                  <h3>
                    Probability Std
                  </h3>

                  <p>
                    {
                      analytics.probability_std.toFixed(3)
                    }
                  </p>
                </div>

              </>
            )
          }

        </div>

      </div>

    </div>
  );
}

export default Visualization;