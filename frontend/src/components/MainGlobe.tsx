import Globe from "react-globe.gl";
import "./MainGlobe.css";

function MainGlobe() {
  return (
    <div className="globe-inner">
    <div className="globe-wrapper">
      <Globe
        width={500}
        height={800}
        animateIn={true}

        globeImageUrl="//unpkg.com/three-globe/example/img/earth-night.jpg"

        bumpImageUrl="//unpkg.com/three-globe/example/img/earth-topology.png"

        backgroundColor="rgba(0,0,0,0)"

        pointsData={[
          {
            lat: 51.5072,
            lng: -0.1276,
            size: 0.35,
          },
          {
            lat: 52.6309,
            lng: 1.2974,
            size: 0.25,
          },
        ]}

        pointAltitude="size"
        pointColor={() => "#00d4ff"}
      />
    </div>
    </div>
  );
}

export default MainGlobe;