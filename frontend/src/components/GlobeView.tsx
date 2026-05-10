import { useEffect, useRef } from "react";
import {
  Viewer as CesiumViewer,
  Ion,
  Cartesian3,
  Color,
  ArcGisMapServerImageryProvider,
  ImageryLayer,
  Entity,
  GeoJsonDataSource,
} from "cesium";

import "cesium/Build/Cesium/Widgets/widgets.css";
import "./GlobeView.css";

Ion.defaultAccessToken = import.meta.env.VITE_CESIUM_TOKEN || "";

const NORWICH = {
  longitude: 1.2974,
  latitude: 52.6309,
};

function GlobeView() {
  const viewerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!viewerRef.current) return;

    const viewer = new CesiumViewer(viewerRef.current, {
      animation: false,
      timeline: false,
      baseLayerPicker: false,
      geocoder: false,
      homeButton: false,
      sceneModePicker: false,
      navigationHelpButton: false,
      infoBox: false,
      selectionIndicator: false,
      fullscreenButton: false,
    });

    ArcGisMapServerImageryProvider.fromUrl(
      "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer"
    ).then((provider) => {
      viewer.imageryLayers.removeAll();

      viewer.imageryLayers.add(
        new ImageryLayer(provider)
      );
    });

    viewer.camera.flyTo({
      destination: Cartesian3.fromDegrees(
        NORWICH.longitude,
        NORWICH.latitude,
        25000
      ),
      duration: 2,
    });

    viewer.entities.add(
      new Entity({
        name: "Norwich",
        position: Cartesian3.fromDegrees(
          NORWICH.longitude,
          NORWICH.latitude
        ),
        point: {
          pixelSize: 10,
          color: Color.CYAN,
        },
      })
    );

    // LOAD ML PREDICTION GEOJSON
    GeoJsonDataSource.load("/data/predicted_map.geojson", {
      stroke: Color.RED,
      fill: Color.RED.withAlpha(0.35),
      strokeWidth: 2,
    }).then((dataSource) => {
      viewer.dataSources.add(dataSource);
      console.log(dataSource.entities.values.length);
    });

    return () => {
      viewer.destroy();
    };
  }, []);

  return (
    <div
      ref={viewerRef}
      className="globe-container"
    />
  );
}

export default GlobeView;