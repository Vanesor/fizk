import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ArrowPathIcon } from "@heroicons/react/24/solid";

export default function LoadingScreen({ message = "Initializing..." }) {
  // Use state to store particle positions - only generated once on the client
  const [particles, setParticles] = useState<
    Array<{
      id: number;
      x: number;
      y: number;
      size: number;
      delay: number;
      duration: number;
      type: string;
    }>
  >([]);

  // Generate particles only on the client side after component mounts
  useEffect(() => {
    // Generate small blue particles
    const smallBlueParticles = Array.from({ length: 30 }).map((_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: 1 + Math.random() * 1.5,
      delay: Math.random() * 2,
      duration: 2 + Math.random() * 4,
      type: "small-blue",
    }));

    // Generate medium cyan particles
    const mediumCyanParticles = Array.from({ length: 20 }).map((_, i) => ({
      id: i + 30,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: 2 + Math.random() * 2,
      delay: Math.random() * 2,
      duration: 3 + Math.random() * 4,
      type: "medium-cyan",
    }));

    // Generate larger teal particles with glow
    const largeGlowParticles = Array.from({ length: 10 }).map((_, i) => ({
      id: i + 50,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: 3 + Math.random() * 2,
      delay: Math.random() * 3,
      duration: 4 + Math.random() * 5,
      type: "glow-teal",
    }));

    setParticles([
      ...smallBlueParticles,
      ...mediumCyanParticles,
      ...largeGlowParticles,
    ]);
  }, []);

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-[#050c1d] via-[#071529] to-[#0c1e35]">
      {/* Enhanced background gradient with more depth */}
      <div
        className="absolute inset-0 z-0"
        style={{
          background:
            "radial-gradient(circle at center, rgba(13,25,45,0.5) 0%, rgba(5,12,24,0.8) 60%, rgba(2,4,10,0.95) 100%)",
        }}
      ></div>

      {/* Glowing center effect */}
      <div
        className="absolute z-5 rounded-full opacity-20 blur-3xl"
        style={{
          width: "40vh",
          height: "40vh",
          background:
            "radial-gradient(circle, rgba(56,189,248,0.3) 0%, rgba(6,182,212,0.1) 50%, rgba(5,12,24,0) 70%)",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          animation: "pulse-slow 4s ease-in-out infinite",
        }}
      />

      {/* Animated particles using pure CSS - CLIENT SIDE ONLY */}
      <div className="absolute inset-0 z-10 overflow-hidden">
        {particles.map((particle) => (
          <div
            key={particle.id}
            className={`absolute rounded-full ${
              particle.type === "small-blue"
                ? "bg-blue-500/40 w-1 h-1"
                : particle.type === "medium-cyan"
                ? "bg-cyan-400/30 w-2 h-2"
                : "bg-teal-300/20 w-3 h-3 blur-sm shadow-lg shadow-cyan-500/30"
            }`}
            style={{
              left: `${particle.x}%`,
              top: `${particle.y}%`,
              width: `${particle.size}px`,
              height: `${particle.size}px`,
              animation: `${
                particle.type === "small-blue"
                  ? "float"
                  : particle.type === "medium-cyan"
                  ? "pulse"
                  : "glow"
              } ${particle.duration}s infinite ease-in-out ${particle.delay}s`,
            }}
          />
        ))}
      </div>

      {/* Enhanced Loading indicator */}
      <div className="relative z-20 flex flex-col items-center text-center">
        <motion.div
          className="bg-gray-900/40 backdrop-blur-xl px-12 py-10 rounded-2xl border border-gray-700/30 shadow-2xl"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          {/* Animated icon container */}
          <motion.div
            className="relative mb-8 mx-auto w-16 h-16"
            animate={{
              rotate: [0, 360],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: "linear",
            }}
          >
            {/* Outer ring */}
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-cyan-500/30"
              animate={{
                scale: [1, 1.1, 1],
                opacity: [0.5, 0.8, 0.5],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />

            {/* Inner ring */}
            <motion.div
              className="absolute inset-2 rounded-full border-2 border-cyan-400/50"
              animate={{
                scale: [1, 1.15, 1],
                opacity: [0.6, 1, 0.6],
              }}
              transition={{
                duration: 2.5,
                repeat: Infinity,
                ease: "easeInOut",
                delay: 0.2,
              }}
            />

            {/* Center icon with glow */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="absolute w-10 h-10 bg-cyan-500/20 rounded-full blur-xl"></div>
              <ArrowPathIcon className="h-8 w-8 text-cyan-400 relative animate-spin" />
            </div>
          </motion.div>

          {/* Message with typing animation effect */}
          <motion.p
            className="text-xl font-medium text-gray-100 tracking-wide"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            {message}
          </motion.p>

          {/* Animated dots */}
          <div className="mt-6 flex justify-center space-x-2">
            {[0, 1, 2].map((dot) => (
              <motion.div
                key={dot}
                className="w-2.5 h-2.5 bg-cyan-500 rounded-full"
                animate={{
                  y: [0, -10, 0],
                  opacity: [0.5, 1, 0.5],
                }}
                transition={{
                  duration: 1.2,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: dot * 0.2,
                }}
              />
            ))}
          </div>
        </motion.div>
      </div>

      {/* Add enhanced CSS animations */}
      <style jsx global>{`
        @keyframes float {
          0%,
          100% {
            transform: translateY(0) translateX(0);
            opacity: 0.3;
          }
          50% {
            transform: translateY(-30px) translateX(15px);
            opacity: 0.7;
          }
        }

        @keyframes pulse {
          0%,
          100% {
            transform: scale(1);
            opacity: 0.2;
          }
          50% {
            transform: scale(1.8);
            opacity: 0.5;
          }
        }

        @keyframes glow {
          0%,
          100% {
            transform: scale(1);
            opacity: 0.3;
            filter: blur(2px);
          }
          50% {
            transform: scale(2.2);
            opacity: 0.7;
            filter: blur(5px);
          }
        }

        @keyframes pulse-slow {
          0%,
          100% {
            opacity: 0.1;
            transform: translate(-50%, -50%) scale(0.9);
          }
          50% {
            opacity: 0.3;
            transform: translate(-50%, -50%) scale(1.1);
          }
        }
      `}</style>
    </div>
  );
}
