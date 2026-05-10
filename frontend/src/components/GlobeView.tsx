import {
  Viewer,
  Entity,
  CameraFlyTo
} from "resium";

import {
  Cartesian3,
  Ion
} from "cesium";

import "cesium/Build/Cesium/Widgets/widgets.css";
import "./GlobeView.css";

Ion.defaultAccessToken = "";

function GlobeView() {
  return (
    <div className="globe-wrapper">
      <Viewer
        full
        animation={false}
        timeline={false}
        baseLayerPicker={false}
        geocoder={false}
        homeButton={false}
        sceneModePicker={false}
        navigationHelpButton={false}
      >
        <CameraFlyTo
          destination={Cartesian3.fromDegrees(
            -0.1276,
            51.5072,
            2500000
          )}
        />

        <Entity
          name="London"
          position={Cartesian3.fromDegrees(
            -0.1276,
            51.5072
          )}
          point={{
            pixelSize: 10
          }}
        />
      </Viewer>
    </div>
  );
}

export default GlobeView;