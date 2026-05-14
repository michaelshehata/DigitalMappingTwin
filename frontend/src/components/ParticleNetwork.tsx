import Particles from "react-tsparticles";
import { loadSlim } from "tsparticles-slim";
import type { Engine } from "tsparticles-engine";

import "./ParticleNetwork.css";

function ParticleNetwork() {
  const particlesInit = async (engine: Engine) => {
    await loadSlim(engine);
  };

  return (
    <div className="particles-wrapper">
      <Particles
        id="tsparticles"
        init={particlesInit}
        options={{
          fullScreen: false,

          background: {
            color: {
              value: "transparent",
            },
          },

          fpsLimit: 60,

          particles: {
            number: {
              value: 45,
            },

            color: {
              value: "#ffffff",
            },

            links: {
              enable: true,
              color: "#888888",
              distance: 120,
              opacity: 0.2,
              width: 1,
            },

            move: {
              enable: true,
              speed: 1,
            },

            opacity: {
              value: 0.4,
            },

            size: {
              value: { min: 1, max: 3 },
            },
          },

          detectRetina: true,
        }}
      />
    </div>
  );
}

export default ParticleNetwork;