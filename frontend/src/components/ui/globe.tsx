"use client";

import { useEffect, useRef } from "react";
import GlobeGL from "globe.gl";

type GlobeProps = {
  globeConfig?: {
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

    const globe = GlobeConstructor()(globeRef.current);

    globe
      // NO REALISTIC EARTH TEXTURE
      .globeImageUrl("//unpkg.com/three-globe/example/img/earth-blue-marble.jpg")

      // TRANSPARENT BG
      .backgroundColor("rgba(0,0,0,0)")

      // ATMOSPHERE GLOW
      .showAtmosphere(true)
      .atmosphereColor("#00d4ff")
      .atmosphereAltitude(0.22);

    globe.controls().autoRotate =
      globeConfig?.autoRotate ?? true;

    globe.controls().autoRotateSpeed =
      globeConfig?.autoRotateSpeed ?? 0.5;

    globe.pointOfView(
      {
        lat: 20,
        lng: 0,
        altitude: 2,
      },
      0
    );

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