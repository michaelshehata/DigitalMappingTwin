import { useState } from "react";
import "./Home.css";
import MainGlobe from "../components/MainGlobe";

function Home() {
  const [videoOk, setVideoOk] = useState(true);

  return (
    <main>
      <div className="video-background">
        {videoOk ? (
          <video
            autoPlay
            loop
            muted
            playsInline
            className="background-video"
            onError={() => setVideoOk(false)}
          >
            <source src="/starry-background.mp4" type="video/mp4" />
          </video>
        ) : null}

        <div className="video-overlay" aria-hidden />
      </div>

      <div className="container">
        <h1>
          Digital <span className="mappingHighlight">Mapping</span> Twin
        </h1>

        <h3>
          A digital twin for mapping land use in <strong>Norwich</strong> over
          the next century!
        </h3>

        <MainGlobe />
      </div>
    </main>
  );
}

export default Home;