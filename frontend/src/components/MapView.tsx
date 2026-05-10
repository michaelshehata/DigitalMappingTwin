import {
  MapContainer,
  TileLayer,
  Marker,
  Popup
} from "react-leaflet";

import "leaflet/dist/leaflet.css";
import "./MapView.css";

function MapView() {
  return (
    <MapContainer
      center={[52.6309, 1.2974]}
      zoom={12}
      className="map-container"
    >

      <TileLayer
        attribution='&copy; OpenStreetMap'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <Marker position={[52.6309, 1.2974]}>
        <Popup>Norwich Simulation Zone</Popup>
      </Marker>

    </MapContainer>
  );
}

export default MapView;