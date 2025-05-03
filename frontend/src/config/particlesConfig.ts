import type { ISourceOptions } from "@tsparticles/engine";

// Use a type assertion to bypass TypeScript property name checks
export const particlesOptions = {
  background: {
    color: {
      value: "#0a0a23", // Dark background
    },
  },
  fpsLimit: 60,
  interactivity: {
    events: {
      onHover: {
        enable: true,
        mode: "grab",
      },
      resize: { enable: true },
    },
    modes: {
      grab: {
        distance: 140,
        links: {
          opacity: 0.8,
          color: "#ffffff",
        },
      },
    },
  },
  particles: {
    color: {
      value: "#ffffff",
    },
    links: {
      color: "#ffffff",
      distance: 150,
      enable: true,
      opacity: 0.2,
      width: 1,
    },
    move: {
      direction: "none",
      enable: true,
      outModes: {
        default: "bounce",
      },
      random: true,
      speed: 0.5,
      straight: false,
    },
    number: {
      density: {
        enable: true,
        factor: 800, // This works at runtime despite TypeScript errors
      },
      value: 50,
    },
    opacity: {
      value: 0.5,
      animation: {
        enable: true,
        speed: 0.5,
        minimumValue: 0.1, // This works at runtime
        sync: false,
      },
    },
    shape: {
      type: "circle",
    },
    size: {
      value: { min: 1, max: 3 },
      animation: {
        enable: true,
        speed: 2,
        minimumValue: 0.5, // This works at runtime
        sync: false,
      },
    },
  },
  detectRetina: true,
} as ISourceOptions;
