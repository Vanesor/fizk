import type { ISourceOptions } from "@tsparticles/engine";

// Enhanced particles configuration
export const particlesOptions = {
  background: {
    color: {
      value: "#060818", // Deeper dark blue for richer background
    },
  },
  particles: {
    number: {
      value: 80,
      density: {
        enable: true,
        factor: 1000,
      },
    },
    color: {
      value: ["#3b82f6", "#06b6d4", "#10b981", "#8b5cf6"], // Added purple for variety
    },
    shape: {
      type: "circle",
    },
    opacity: {
      value: { min: 0.1, max: 0.5 },
      animation: {
        enable: true,
        speed: 1,
        minimumValue: 0.1,
        sync: false,
      },
    },
    size: {
      value: { min: 1, max: 3 },
      animation: {
        enable: true,
        speed: 2,
        minimumValue: 0.5,
        sync: false,
      },
    },
    links: {
      enable: true,
      distance: 150,
      color: "#304566", // More subtle links
      opacity: 0.3,
      width: 1,
      // Add subtle glow to links for more tech feel
      shadow: {
        enable: true,
        color: "#48b0f9",
        blur: 5,
      },
      // Make link triangulation more dynamic
      triangles: {
        enable: true,
        frequency: 0.05,
        opacity: 0.05,
      },
    },
    move: {
      enable: true,
      speed: 0.8,
      direction: "none",
      random: true,
      straight: false,
      outModes: {
        default: "out",
      },
      // Add slight attraction for more organic clustering
      attract: {
        enable: true,
        rotateX: 600,
        rotateY: 1200,
      },
    },
  },
  interactivity: {
    detectsOn: "window",
    events: {
      onHover: {
        enable: true,
        mode: "grab",
      },
      onClick: {
        enable: true,
        mode: "push", // Add new particles on click
      },
      // Fix: Change boolean to object with enable property
      resize: {
        enable: true,
      },
    },
    modes: {
      grab: {
        distance: 180,
        links: {
          opacity: 0.5,
          color: "#48b0f9",
        },
      },
      push: {
        quantity: 1, // Number of particles to add on click
      },
      // Add repulse mode for more interactivity
      repulse: {
        distance: 100,
        duration: 0.4,
      },
    },
  },
  detectRetina: true,
  // Add subtle motion blur for smoother animation
  motion: {
    reduce: {
      factor: 0.5,
      value: true,
    },
  },
  // Particles will have a slight glow
  emitters: {
    direction: "top",
    rate: {
      delay: 5,
      quantity: 1,
    },
    size: {
      width: 100,
      height: 0,
    },
    position: {
      x: 50,
      y: 100,
    },
  },
  // Improved performance settings
  fpsLimit: 120,
} as unknown as ISourceOptions; // Use unknown first to bypass type checking

// Add a second particles configuration with glowing nodes for login page
export const loginParticlesOptions = {
  ...particlesOptions,
  particles: {
    ...particlesOptions.particles,
    number: {
      value: 60,
      density: {
        enable: true,
        factor: 1200,
      },
    },
    color: {
      value: ["#0ea5e9", "#22d3ee", "#2dd4bf"], // Sky, cyan, teal for login
    },
    shape: {
      type: ["circle", "triangle"],
    },
  },
} as unknown as ISourceOptions;
