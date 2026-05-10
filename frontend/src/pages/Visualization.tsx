import "./Visualization.css";
import MapView from "../components/MapView.tsx";
import ScenarioPanel from "../components/ScenarioPanel.tsx";
import AnalyticsPanel from "../components/AnalyticsPanel.tsx";

function Visualization() {
  return (
    <div className="visualization-layout">

      <aside className="left-panel">
        <ScenarioPanel />
      </aside>

      <main className="map-panel">
        <MapView />
      </main>

      <aside className="right-panel">
        <AnalyticsPanel />
      </aside>

    </div>
  );
}

export default Visualization;