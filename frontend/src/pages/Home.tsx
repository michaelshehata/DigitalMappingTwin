import { useState } from "react";
import "./Home.css";

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
        <h1>Digital Mapping Twin</h1>
        <h3>A digital twin for mapping land use over the next century!</h3>
      </div>
    </main>
  );
}

export default Home;
