import { Routes, Route } from "react-router-dom";
import "./App.css";

import Header from "./components/Header";
import Footer from "./components/Footer";

import Home from "./pages/Home";
import About from "./pages/About";
import Analysis from "./pages/Analysis";
import Data from "./pages/Data";
import Visualization from "./pages/Visualization";

function App() {
  return (
    <div className="app">

      <Header />

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/visualization" element={<Visualization />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/data" element={<Data />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>

      <Footer />

    </div>
  );
}

export default App;