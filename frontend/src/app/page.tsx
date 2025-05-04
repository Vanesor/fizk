"use client";

import { useState, useEffect, useMemo } from "react";
import { motion } from "framer-motion";
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  EyeIcon,
  EyeSlashIcon,
  KeyIcon,
} from "@heroicons/react/24/solid";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Particles, { initParticlesEngine } from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import type { Container } from "@tsparticles/engine";
import { particlesOptions } from "@/config/particlesConfig";
import LoadingScreen from "@/components/LoadingScreen";
import { SchnorrAuth } from "@/utils/schnorr";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

const renderMessage = (msg: unknown) => {
  if (typeof msg === "string") return msg;
  try {
    return JSON.stringify(msg);
  } catch {
    return String(msg);
  }
};

export default function LoginPage() {
  const [init, setInit] = useState(false);
  const [particlesInitialized, setParticlesInitialized] = useState(false);
  const [mnemonicInput, setMnemonicInput] = useState("");
  const [isMnemonicVisible, setIsMnemonicVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const router = useRouter();

  useEffect(() => {
    let isMounted = true;
    const safetyTimeout = setTimeout(() => {
      if (isMounted && !init) setInit(true);
    }, 5000);
    const initialize = async () => {
      try {
        setInit(true);
        if (!particlesInitialized) {
          await initParticlesEngine(async (engine) => {
            await loadSlim(engine);
          });
          if (isMounted) setParticlesInitialized(true);
        }
      } catch (err) {
        console.error("Error initializing particles:", err);
      }
    };
    initialize();
    return () => {
      isMounted = false;
      clearTimeout(safetyTimeout);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const particlesInit = async (container?: Container): Promise<void> => {};

  const ParticlesBackground = useMemo(
    () => (
      <Particles
        id="tsparticles-login"
        particlesLoaded={particlesInit}
        options={particlesOptions}
        className="absolute inset-0 z-0"
      />
    ),
    []
  );

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg("");
    setSuccessMsg("");

    try {
      console.group("🔒 Login Process");
      console.log("Starting Schnorr ZKP authentication...");

      const mnemonic = mnemonicInput.trim();
      const { privateKey, publicKey } =
        await SchnorrAuth.deriveKeyPairFromMnemonic(mnemonic);

      const result = await SchnorrAuth.authenticate(
        API_BASE_URL,
        privateKey,
        publicKey
      );

      setSuccessMsg(
        `Welcome back, ${result.username || "user"}! Redirecting...`
      );
      console.log("✅ Authentication successful! Redirecting...");
      console.groupEnd();

      setMnemonicInput("");

      setTimeout(() => router.push("/home"), 1500);
    } catch (err: unknown) {
      console.error("❌ Authentication failed:", err);
      console.groupEnd();

      if (err instanceof Error) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg(
          "Authentication failed. Please check your recovery phrase and try again."
        );
      }

      setMnemonicInput("");
    } finally {
      setIsLoading(false);
    }
  }

  if (!init) {
    return <LoadingScreen message="Initializing..." />;
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-gray-900 to-gray-800 p-6 font-sans">
      {ParticlesBackground}
      <div className="absolute inset-0 bg-black/40 z-0"></div>

      <div className="relative z-10 w-full max-w-sm flex flex-col items-center">
        <div className="mb-10 flex items-center justify-center">
          <div className="p-4 bg-blue-500/10 rounded-full">
            <KeyIcon className="h-12 w-12 text-blue-400" />
          </div>
        </div>

        <motion.div
          className="w-full bg-gray-50 dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 p-8 md:p-10"
          initial={{ opacity: 0, y: -15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        >
          <h1 className="text-2xl font-semibold text-center text-gray-900 dark:text-white mb-10">
            Sign in to your account
          </h1>

          <form onSubmit={handleLogin} className="space-y-8">
            <div className="space-y-3">
              <label
                htmlFor="mnemonic"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2.5"
              >
                Recovery Phrase
              </label>
              <div className="relative">
                <input
                  id="mnemonic"
                  value={mnemonicInput}
                  onChange={(e) => setMnemonicInput(e.target.value)}
                  className={`block w-full h-10 p-4 border rounded-lg shadow-sm 
                             bg-gray-100 dark:bg-gray-700 
                             text-gray-900 dark:text-gray-100 
                             placeholder-gray-400 dark:placeholder-gray-500 
                             border-gray-300 dark:border-gray-600 
                             font-mono text-sm resize-none transition-all duration-200
                             hover:border-blue-400 dark:hover:border-blue-500
                             focus:border-blue-500 focus:ring-4 focus:ring-blue-500/30 focus:ring-opacity-50 dark:focus:border-blue-400 dark:focus:ring-blue-400/20
                             ${isMnemonicVisible ? "" : "blur-[3px]"}`}
                  placeholder="Enter your 12-word recovery phrase..."
                  spellCheck="false"
                  required
                  readOnly={isLoading}
                  style={{ filter: isMnemonicVisible ? "none" : "blur(3px)" }}
                />
                <button
                  type="button"
                  onClick={() => setIsMnemonicVisible(!isMnemonicVisible)}
                  className="absolute bottom-10 right-3 p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 rounded-md bg-gray-200/50 dark:bg-gray-600/50 hover:bg-gray-300/70 dark:hover:bg-gray-500/70 transition-colors duration-150"
                  aria-label={isMnemonicVisible ? "Hide phrase" : "Show phrase"}
                >
                  {isMnemonicVisible ? (
                    <EyeSlashIcon className="h-5 w-5 " />
                  ) : (
                    <EyeIcon className="h-5 w-5" />
                  )}
                </button>
              </div>
              <p className="mt-3 text-xs text-gray-500 dark:text-gray-400 px-1">
                Enter the 12 words in the correct order.
              </p>
            </div>
            <div className="h-6 text-center text-sm pt-2 pb-3">
              {errorMsg && (
                <p className="text-red-600 dark:text-red-400 flex items-center justify-center text-xs">
                  <ExclamationTriangleIcon className="w-4 h-4 mr-2 inline" />
                  {renderMessage(errorMsg)}
                </p>
              )}
              {successMsg && (
                <p className="text-green-600 dark:text-green-400 flex items-center justify-center text-xs">
                  <CheckCircleIcon className="w-4 h-4 mr-2 inline" />
                  {renderMessage(successMsg)}
                </p>
              )}
            </div>
            <motion.button
              type="submit"
              disabled={isLoading || !mnemonicInput}
              className="w-full flex justify-center items-center 
                         bg-gradient-to-r from-blue-600 to-blue-500
                         hover:from-blue-500 hover:to-blue-400 
                         disabled:from-blue-400 disabled:to-blue-300 dark:disabled:from-blue-800 dark:disabled:to-blue-700 
                         disabled:opacity-70 disabled:cursor-not-allowed 
                         text-white py-4 px-6 rounded-lg shadow-lg 
                         text-base font-medium 
                         focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-offset-gray-800 
                         transition-all duration-200 ease-out mt-4"
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
            >
              {isLoading ? (
                <>
                  <ArrowPathIcon className="animate-spin h-5 w-5 mr-2.5" />
                  Signing In...
                </>
              ) : (
                "Sign In"
              )}
            </motion.button>
          </form>
        </motion.div>

        <motion.div
          className="w-full mt-8 border border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center bg-gray-50 dark:bg-gray-800/50"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2, ease: "easeOut" }}
        >
          <p className="text-sm text-gray-700 dark:text-gray-300">
            New here?{" "}
            <Link
              href="/signup"
              className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300 hover:underline"
            >
              Create an account
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
