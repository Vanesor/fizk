// import type { ISourceOptions } from "@tsparticles/engine";

// // Enhanced particles configuration
// export const particlesOptions = {
//   background: {
//     color: {
//       value: "#060818", // Deeper dark blue for richer background
//     },
//   },
//   particles: {
//     number: {
//       value: 80,
//       density: {
//         enable: true,
//         factor: 1000,
//       },
//     },
//     color: {
//       // Using slightly brighter shades
//       value: ["#60a5fa", "#22d3ee", "#34d399", "#a78bfa"],
//     },
//     shape: {
//       type: "circle",
//     },
//     opacity: {
//       // Increased minimum opacity for brighter appearance
//       value: { min: 0.3, max: 0.7 },
//       animation: {
//         enable: true,
//         speed: 1,
//         minimumValue: 0.2, // Slightly higher minimum during animation
//         sync: false,
//       },
//     },
//     size: {
//       // Slightly larger max size
//       value: { min: 1, max: 4 },
//       animation: {
//         enable: true,
//         speed: 2,
//         minimumValue: 0.5,
//         sync: false,
//       },
//     },
//     links: {
//       enable: true,
//       distance: 150,
//       // Brighter link color
//       color: "#5fa8d3", // Lighter blue for links
//       // Increased link opacity
//       opacity: 0.5,
//       width: 1,
//       shadow: {
//         enable: true,
//         // Brighter shadow color
//         color: "#60a5fa",
//         // Slightly increased blur for a softer glow
//         blur: 7,
//       },
//       triangles: {
//         enable: true,
//         frequency: 0.05,
//         // Slightly increased triangle opacity
//         opacity: 0.08,
//       },
//     },
//     move: {
//       enable: true,
//       speed: 0.8,
//       direction: "none",
//       random: true,
//       straight: false,
//       outModes: {
//         default: "out",
//       },
//       attract: {
//         enable: true,
//         rotateX: 600,
//         rotateY: 1200,
//       },
//     },
//   },
//   interactivity: {
//     detectsOn: "window",
//     events: {
//       onHover: {
//         enable: true,
//         mode: "grab",
//       },
//       onClick: {
//         enable: true,
//         mode: "push",
//       },
//       resize: {
//         enable: true,
//       },
//     },
//     modes: {
//       grab: {
//         distance: 180,
//         links: {
//           // Brighter grab link color
//           opacity: 0.7,
//           color: "#60a5fa",
//         },
//       },
//       push: {
//         quantity: 1,
//       },
//       repulse: {
//         distance: 100,
//         duration: 0.4,
//       },
//     },
//   },
//   detectRetina: true,
//   motion: {
//     reduce: {
//       factor: 0.5,
//       value: true,
//     },
//   },
//   emitters: {
//     direction: "top",
//     rate: {
//       delay: 5,
//       quantity: 1,
//     },
//     size: {
//       width: 100,
//       height: 0,
//     },
//     position: {
//       x: 50,
//       y: 100,
//     },
//   },
//   fpsLimit: 120,
// } as unknown as ISourceOptions;

// // Add a second particles configuration with glowing nodes for login page
// export const loginParticlesOptions = {
//   ...particlesOptions, // Inherit base brightness settings
//   particles: {
//     ...particlesOptions.particles,
//     number: {
//       value: 60,
//       density: {
//         enable: true,
//         factor: 1200,
//       },
//     },
//     // Using brighter versions of the login colors
//     color: {
//       value: ["#38bdf8", "#22d3ee", "#5eead4"],
//     },
//     shape: {
//       type: ["circle", "triangle"],
//     },
//     // Inherit opacity and size from the updated base particlesOptions
//     // Inherit links settings (color, opacity, shadow) from base
//   },
//   // Inherit interactivity settings, including brighter grab links
// } as unknown as ISourceOptions;

import type { ISourceOptions } from "@tsparticles/engine";

// Enhanced particles configuration with significantly increased brightness (+0.5 more)
export const particlesOptions = {
  background: {
    color: {
      value: "#040610", // Even darker background for more contrast
    },
  },
  particles: {
    number: {
      value: 70, // Maintain for performance
      density: {
        enable: true,
        factor: 1000,
      },
    },
    color: {
      // Using extremely bright shades - increased by another 0.5
      value: [
        "#dbeafe", // Very bright blue (almost white)
        "#a5f3fc", // Very bright cyan
        "#9aeabc", // Very bright green
        "#e9d5ff", // Very bright purple
        "#ffffff", // Pure white (more dominant)
      ],
    },
    shape: {
      type: "circle", // Keep for efficiency
    },
    opacity: {
      // Further increased opacity for maximum brightness
      value: { min: 0.65, max: 1.0 }, // +0.25 to min, max at full
      animation: {
        enable: true,
        speed: 0.8, // Same for performance
        minimumValue: 0.5, // +0.2 compared to previous
        sync: false,
      },
    },
    size: {
      // Slightly larger for more brightness impression
      value: { min: 1.2, max: 4.5 }, // Increased min size
      animation: {
        enable: true,
        speed: 1.5, // Same for performance
        minimumValue: 0.8, // Increased
        sync: false,
      },
    },
    links: {
      enable: true,
      distance: 150,
      // Maximally bright link color
      color: "#dbeafe", // Almost white blue
      // Maximum practical opacity
      opacity: 0.85, // +0.25 for maximum visibility
      width: 1.2, // Slightly thicker
      shadow: {
        enable: true,
        // Pure white shadow for maximum glow
        color: "#ffffff", // Pure white for stronger glow
        // Maximum practical blur
        blur: 12, // +4 for much stronger glow
      },
      triangles: {
        enable: true,
        frequency: 0.04, // Same for performance
        opacity: 0.2, // +0.1 for more visibility
      },
    },
    move: {
      enable: true,
      speed: 0.6, // Same for performance
      direction: "none",
      random: true,
      straight: false,
      outModes: {
        default: "out",
      },
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
        mode: "push",
      },
      resize: {
        enable: true,
      },
    },
    modes: {
      grab: {
        distance: 160, // Same for performance
        links: {
          // Maximum brightness links on hover
          opacity: 1.0, // Full opacity
          color: "#ffffff", // Pure white
        },
      },
      push: {
        quantity: 1, // Same for performance
      },
      repulse: {
        distance: 100,
        duration: 0.4,
      },
    },
  },
  detectRetina: true,
  fpsLimit: 30, // Keep 30 FPS for performance
  motion: {
    reduce: {
      factor: 0.7, // Same for performance
      value: true,
    },
  },
  emitters: {
    direction: "top",
    rate: {
      delay: 8, // Same for performance
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
} as unknown as ISourceOptions;

// Login particles with extreme brightness
export const loginParticlesOptions = {
  ...particlesOptions,
  particles: {
    ...particlesOptions.particles,
    number: {
      value: 60, // Same for performance
      density: {
        enable: true,
        factor: 1200,
      },
    },
    // Using extremely bright colors (nearly white)
    color: {
      value: [
        "#bfdbfe", // Very bright sky blue
        "#a5f3fc", // Very bright cyan
        "#ffffff", // Pure white (most dominant)
        "#f0f9ff", // Almost white blue
        "#f9fafb", // Nearly white
      ],
    },
    shape: {
      type: ["circle"], // Keep circles for efficiency
    },
    opacity: {
      // Maximum practical opacity
      value: { min: 0.8, max: 1.0 }, // Almost full opacity throughout
    },
    links: {
      // Overriding inherited links for maximum brightness
      enable: true,
      distance: 150,
      color: "#ffffff", // Pure white links
      opacity: 0.9, // Nearly full opacity
      width: 1.3, // Slightly thicker for visibility
      shadow: {
        enable: true,
        color: "#ffffff", // Pure white glow
        blur: 15, // Maximum practical glow
      },
      triangles: {
        enable: true,
        frequency: 0.04,
        opacity: 0.25, // Higher triangle opacity
      },
    },
    size: {
      // Larger particles for login
      value: { min: 1.5, max: 5 }, // Larger min and max
    },
  },
} as unknown as ISourceOptions;
