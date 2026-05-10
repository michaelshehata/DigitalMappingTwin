import "./Visualization.css";

import Header from "../components/Header";
import Footer from "../components/Footer";

import ScenarioPanel from "../components/ScenarioPanel";
import AnalyticsPanel from "../components/AnalyticsPanel";
import GlobeView from "../components/GlobeView";

function Visualization() {
  return (
    <div className="visualization-page">

      <Header />

      <main className="visualization-layout">

        <aside className="left-panel">
          <ScenarioPanel />
        </aside>

        <section className="center-panel">
          <GlobeView />
        </section>

        <aside className="right-panel">
          <AnalyticsPanel />
        </aside>

      </main>

      <Footer />

    </div>
  );
}

export default Visualization;