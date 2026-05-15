"use client";

import { useEffect, useRef } from "react";
import GlobeGL from "globe.gl";
import countries from "../../data/globe.json";

type GlobeProps = {
  globeConfig?: {
    globeColor?: string;
    autoRotate?: boolean;
    autoRotateSpeed?: number;
  };
};

export function Globe({ globeConfig }: GlobeProps) {
  const globeRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!globeRef.current) return;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const GlobeConstructor = GlobeGL as any;

    const globe = GlobeConstructor()(globeRef.current)
      .globeImageUrl(
        "//unpkg.com/three-globe/example/img/earth-dark.jpg"
      )
      .backgroundColor("rgba(0,0,0,0)")
      .polygonsData(countries.features)
      .polygonCapColor(
        () => globeConfig?.globeColor || "#062056"
      )
      .polygonSideColor(
        () => "rgba(255,255,255,0.05)"
      )
      .polygonStrokeColor(() => "#111")
      .polygonAltitude(0.01);

    globe.controls().autoRotate =
      globeConfig?.autoRotate ?? true;

    globe.controls().autoRotateSpeed =
      globeConfig?.autoRotateSpeed ?? 0.5;

    return () => {
      globe._destructor();
    };
  }, [globeConfig]);

  return (
    <div
      ref={globeRef}
      style={{
        width: "100%",
        height: "100%",
      }}
    />
  );
}