import "./Home.css";

function Home() {
  return (
    <main>
      <div className="video-background">
        <video autoPlay loop muted playsInline className="background-video">
          <source src="/starry-background.mp4" type="video/mp4" />
        </video>
        <div className="video-overlay" />
      </div>

      <div className="container">
        <h1>Digital Twin</h1>
        <h3>A digital twin for mapping land use over the next century</h3>
      </div>
    </main>
  );
}

export default Home;
