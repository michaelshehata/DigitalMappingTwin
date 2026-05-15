"use client";

import { Globe } from "./ui/globe";
import "./MainGlobe.css";

export default function MainGlobe() {
  const globeConfig = {
    globeColor: "#062056",
    autoRotate: true,
    autoRotateSpeed: 0.5,
  };

  return (
    <div className="globe-wrapper">
      <div className="globe-inner">
        <Globe globeConfig={globeConfig} />
      </div>
    </div>
  );
}