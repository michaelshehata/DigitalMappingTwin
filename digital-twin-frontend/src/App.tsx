import './App.css'
import Header from './components/Header'

function App() {
  return (
    <>
      <Header />
      
      {/* Video Background */}
      <div className="video-background">
        <video autoPlay loop muted playsInline className="background-video">
          <source src="/starry-background.mp4" type="video/mp4" />
        </video>
        <div className="video-overlay"></div>
      </div>

      {/* Content - h1 and h3 INSIDE container */}
      <div className="container">
        <h1>Digital Twin</h1>
        <h3>A digital twin for mapping land use over the next century</h3>
      </div>
    </>
  )
}

export default App