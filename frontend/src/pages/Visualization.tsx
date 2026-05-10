import "./Visualization.css";

import MapView from "../components/MapView";
import ScenarioPanel from "../components/ScenarioPanel";
import AnalyticsPanel from "../components/AnalyticsPanel";

function Visualization() {
  return (
    <div className="visualization-page">

      <div className="visualization-grid">

        <aside className="visual-panel">
          <ScenarioPanel />
        </aside>

        <section className="map-section">
          <MapView />
        </section>

        <aside className="visual-panel">
          <AnalyticsPanel />
        </aside>

      </div>

    </div>
  );
}

export default Visualization;