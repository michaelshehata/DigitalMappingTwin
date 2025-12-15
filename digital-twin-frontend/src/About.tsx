import './App.css'
import Header from './components/Header'

function About() {
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

      
      <div className="container">
        <h1>About</h1>
        <h3>A deeper dive into the project</h3>
      </div>
    </>
  )
}

export default About