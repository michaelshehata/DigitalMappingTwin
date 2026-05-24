import { useEffect, useState } from "react";

import {
  MapContainer,
  TileLayer,
  ImageOverlay,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";
import "./Visualization.css";

/*
  Norwich Bounds
*/

const imageBounds: [
  [number, number],
  [number, number]
] = [
  [52.56, 1.18],
  [52.70, 1.42],
];

function VisualizationPage() {

  /*
    Slider State
  */

  const [sliderValue, setSliderValue] =
    useState(1);

  /*
    Active Forecast Year
  */

  const [activeYear, setActiveYear] =
    useState(2034);

  /*
    Last Updated State
  */

  const [lastUpdated, setLastUpdated] =
    useState("--");

  /*
    Year Calculation
  */

  const simulationYear =
    2024 + (sliderValue * 10);

  /*
    Live Data State
  */

  const [liveData, setLiveData] =
    useState({

      temperature: "--",

      rainfall: "--",

      windSpeed: "--",

      humidity: "--",

      floodRisk: "--",

      elevation: "27m ASL",

    });

  /*
    Live API Fetch
  */

  useEffect(() => {

    async function fetchLiveData() {

      try {

        /*
          WEATHER DATA
        */

        const weatherResponse =
          await fetch(
            "https://api.open-meteo.com/v1/forecast?latitude=52.6309&longitude=1.2974&current=temperature_2m,precipitation,windspeed_10m,relative_humidity_2m"
          );

        const weatherData =
          await weatherResponse.json();

        /*
          FLOOD DATA
        */

        const floodResponse =
          await fetch(
            "https://environment.data.gov.uk/flood-monitoring/id/stations"
          );

        const floodData =
          await floodResponse.json();

        /*
          UPDATE STATE
        */

        setLiveData({

          temperature:
            weatherData.current
              ?.temperature_2m ?? "--",

          rainfall:
            weatherData.current
              ?.precipitation ?? "--",

          windSpeed:
            weatherData.current
              ?.windspeed_10m ?? "--",

          humidity:
            weatherData.current
              ?.relative_humidity_2m ?? "--",

          floodRisk:
            floodData.items?.length
              ? "Monitoring"
              : "Low",

          elevation: "27m ASL",

        });

        /*
          LAST UPDATED TIME
        */

        const now = new Date();

        setLastUpdated(

          now.toLocaleTimeString(
            [],
            {
              hour: "2-digit",
              minute: "2-digit",
            }
          )

        );

      } catch (error) {

        console.error(
          "Failed to fetch live data",
          error
        );

      }

    }

    fetchLiveData();

    const interval =
      setInterval(
        fetchLiveData,
        60000
      );

    return () =>
      clearInterval(interval);

  }, []);

  /*
    Generate Prediction
  */

  const generatePrediction = () => {

    setActiveYear(
      simulationYear
    );

  };

  return (

    <main className="dtVisualizationPage">

      <div className="dtVisualizationBackgroundOverlay" />

      <div className="dtVisualizationDashboardLayout">

        {/* LEFT SIDEBAR */}

        <section className="dtSimulationSidebar">

          <div className="dtPanelGlassContainer">

            <h2 className="dtSidebarTitle">
              Simulation Controls
            </h2>

            <div className="dtSidebarSection">

              <label className="dtSidebarLabel">
                Simulation Year
              </label>

              <div className="dtYearValueDisplay">
                {simulationYear}
              </div>

              <input
                type="range"
                min="0"
                max="10"
                step="1"
                value={sliderValue}
                onChange={(e) =>
                  setSliderValue(
                    Number(e.target.value)
                  )
                }
                className="dtSimulationYearSlider"
              />

              <div className="dtSliderYearMarkers">
                <span>2024</span>
                <span>2124</span>
              </div>

            </div>

            <button
              className="dtGeneratePredictionButton"
              onClick={
                generatePrediction
              }
            >
              Generate Prediction
            </button>

            {/* LAND COVER LEGEND */}

            <div className="dtLegendContainer">

              <h3 className="dtLegendTitle">
                Land Use Key
              </h3>

              <div className="dtLegendList">

                <div className="dtLegendItem">
                  <span
                    className="dtLegendColour"
                    style={{
                      background: "#2e7d32"
                    }}
                  />
                  <span>Vegetation</span>
                </div>

                <div className="dtLegendItem">
                  <span
                    className="dtLegendColour"
                    style={{
                      background: "#fdd835"
                    }}
                  />
                  <span>Agricultural</span>
                </div>

                <div className="dtLegendItem">
                  <span
                    className="dtLegendColour"
                    style={{
                      background: "#d32f2f"
                    }}
                  />
                  <span>Urban</span>
                </div>

                <div className="dtLegendItem">
                  <span
                    className="dtLegendColour"
                    style={{
                      background: "#1565c0"
                    }}
                  />
                  <span>Water</span>
                </div>

                <div className="dtLegendItem">
                  <span
                    className="dtLegendColour"
                    style={{
                      background: "#8d6e63"
                    }}
                  />
                  <span>Sparse</span>
                </div>

              </div>

            </div>

          </div>

        </section>

        {/* MAP */}

        <section className="dtMapVisualizationSection">

          <div className="dtPanelGlassContainer dtMapPanelContainer">

            <div className="dtMapPanelHeader">

              <div>

                <h2 className="dtMapTitle">
                  Norwich Digital Twin
                </h2>

                <p className="dtMapSubtitle">
                  Interactive Environmental Projection
                </p>

              </div>

              <div className="dtProjectionYearBadge">
                {activeYear}
              </div>

            </div>

            <div className="dtLeafletMapWrapper">

              <MapContainer
                center={[52.6309, 1.2974]}
                zoom={11}
                scrollWheelZoom={true}
                className="dtLeafletMap"
              >

                <TileLayer
                  attribution="&copy; OpenStreetMap contributors"
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                <ImageOverlay
                  url={`/forecasts/forecast_${activeYear}.png`}
                  bounds={imageBounds}
                  opacity={0.72}
                />

              </MapContainer>

            </div>

          </div>

        </section>

        {/* RIGHT SIDEBAR */}

        <section className="dtLiveDataSidebar">

          <div className="dtPanelGlassContainer">

            <div className="dtLiveDataHeader">

              <h2 className="dtLiveDataTitle">
                Live Data
              </h2>

              <span className="dtLastUpdatedText">
                Updated: {lastUpdated}
              </span>

            </div>

            <div className="dtLiveMetricGrid">

              <div className="dtLiveMetricCard">

                <h3>
                  Temperature
                </h3>

                <p>
                  {liveData.temperature}°C
                </p>

              </div>

              <div className="dtLiveMetricCard">

                <h3>
                  Rainfall
                </h3>

                <p>
                  {liveData.rainfall} mm
                </p>

              </div>

              <div className="dtLiveMetricCard">

                <h3>
                  Wind Speed
                </h3>

                <p>
                  {liveData.windSpeed} km/h
                </p>

              </div>

              <div className="dtLiveMetricCard">

                <h3>
                  Humidity
                </h3>

                <p>
                  {liveData.humidity}%
                </p>

              </div>

              <div className="dtLiveMetricCard">

                <h3>
                  Flood Status
                </h3>

                <p>
                  {liveData.floodRisk}
                </p>

              </div>

              <div className="dtLiveMetricCard">

                <h3>
                  Elevation
                </h3>

                <p>
                  {liveData.elevation}
                </p>

              </div>

            </div>

          </div>

        </section>

      </div>

    </main>
  );
}

export default VisualizationPage;