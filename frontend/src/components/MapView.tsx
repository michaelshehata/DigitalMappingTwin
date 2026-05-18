import {
  MapContainer,
  TileLayer,
  ImageOverlay,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

import "./MapView.css";

type Props = {
  showProbability: boolean;
  showBinary: boolean;
  showNDVI: boolean;
};

function MapView({
  showProbability,
  showBinary,
  showNDVI,
}: Props) {

  const bounds = [
    [52.55, 1.05],
    [52.88, 1.55],
  ];

  return (

    <div className="globe-container">

      <MapContainer
        center={[52.72, 1.30]}
        zoom={11}
        style={{
          height: "100%",
          width: "100%",
        }}
      >

        <TileLayer
          attribution="OpenStreetMap"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {showNDVI && (
          <ImageOverlay
            url="/rasters/ndvi.png"
            bounds={bounds}
            opacity={0.6}
          />
        )}

        {showProbability && (
          <ImageOverlay
            url="/rasters/probability.png"
            bounds={bounds}
            opacity={0.75}
          />
        )}

        {showBinary && (
          <ImageOverlay
            url="/rasters/binary.png"
            bounds={bounds}
            opacity={0.55}
          />
        )}

      </MapContainer>

    </div>
  );
}

export default MapView;