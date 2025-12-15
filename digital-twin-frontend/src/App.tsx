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
    <>
      <Header />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/analysis" element={<Analysis />} />
        <Route path="/data" element={<Data />} />
        <Route path="/visualization" element={<Visualization />} />
      </Routes>

      <Footer />
    </>
  );
}

export default App;
