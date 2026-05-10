import { Viewer } from "resium";
import { Ion } from "cesium";

import "cesium/Build/Cesium/Widgets/widgets.css";
import "./GlobeView.css";

Ion.defaultAccessToken = import.meta.env.VITE_MAPBOX_TOKEN || "";

function GlobeView() {
  return (
    <div className="globe-container">
      <Viewer
        className="cesium-viewer-custom"
        full={false}
        animation={false}
        timeline={false}
        baseLayerPicker={false}
        geocoder={false}
        homeButton={false}
        sceneModePicker={false}
        navigationHelpButton={false}
        infoBox={false}
        selectionIndicator={false}
        fullscreenButton={false}
      />
    </div>
  );
}

export default GlobeView;