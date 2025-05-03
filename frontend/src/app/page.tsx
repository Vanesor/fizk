"use client";

import { useState, useEffect, useMemo } from "react";
import axios from "axios";
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
import * as bip39 from "bip39";
import { ec as EC } from "elliptic";
import { sha256 } from "@noble/hashes/sha2";
import { bytesToHex } from "@noble/hashes/utils";
import { getPublicKey } from "@noble/secp256k1";
import Particles, { initParticlesEngine } from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import type { Container } from "@tsparticles/engine";
import { particlesOptions } from "@/config/particlesConfig";
import LoadingScreen from "@/components/LoadingScreen";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
const ec = new EC("secp256k1");

// Helper functions (remain the same)
const hexToBytes = (hex: string): Uint8Array => {
  if (hex.length % 2 !== 0) throw new Error("Invalid hex string length.");
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substring(i, i + 2), 16);
  }
  return bytes;
};

const renderMessage = (msg: unknown) => {
  if (typeof msg === "string") return msg;
  try {
    return JSON.stringify(msg);
  } catch {
    return String(msg);
  }
};
// --- End Helper Functions ---

export default function LoginPage() {
  // State and Hooks (remain the same)
  const [init, setInit] = useState(false);
  const [particlesInitialized, setParticlesInitialized] = useState(false);
  const [mnemonicInput, setMnemonicInput] = useState("");
  const [isMnemonicVisible, setIsMnemonicVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const router = useRouter();

  // useEffects and other functions (remain the same)
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
    let privateKeyBytes: Uint8Array;
    let publicKeyHex: string;
    try {
      const mnemonic = mnemonicInput.trim();
      if (!bip39.validateMnemonic(mnemonic))
        throw new Error("Invalid recovery phrase.");
      const seed = await bip39.mnemonicToSeed(mnemonic);
      privateKeyBytes = new Uint8Array(seed).slice(0, 32);
      const pubBytes = getPublicKey(privateKeyBytes, true);
      publicKeyHex = bytesToHex(pubBytes);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : renderMessage(err));
      setIsLoading(false);
      setMnemonicInput("");
      return;
    }
    let challengeHex: string;
    try {
      const res = await axios.post<{ challengeHex: string }>(
        `${API_BASE_URL}/api/auth/challenge`,
        { pubkey: publicKeyHex }
      );
      challengeHex = res.data.challengeHex;
      if (!challengeHex || challengeHex.length !== 64)
        throw new Error("Received invalid challenge from server.");
    } catch (err: unknown) {
      const msg = axios.isAxiosError(err)
        ? err.response?.data?.detail || `Server Error: ${err.response?.status}`
        : err instanceof Error
        ? err.message
        : "Failed to get challenge";
      setErrorMsg(renderMessage(msg));
      setIsLoading(false);
      setMnemonicInput("");
      return;
    }
    let signatureDER: string;
    try {
      const privateKeyInt = BigInt("0x" + bytesToHex(privateKeyBytes));
      const keyPair = ec.keyFromPrivate(privateKeyInt.toString(16), "hex");
      const challengeBytes = hexToBytes(challengeHex);
      const challengeHash = sha256(challengeBytes);
      const signature = keyPair.sign(challengeHash);
      signatureDER = signature.toDER("hex");
    } catch (err: unknown) {
      setErrorMsg(
        err instanceof Error
          ? `Signing error: ${err.message}`
          : "Failed to sign challenge"
      );
      setIsLoading(false);
      return;
    }
    setMnemonicInput("");
    try {
      const loginRes = await axios.post(`${API_BASE_URL}/api/auth/login`, {
        pubkey: publicKeyHex,
        signature_der: signatureDER,
        challengeHex: challengeHex,
      });
      if (loginRes.data.success) {
        setSuccessMsg(`Authentication successful! Redirecting...`);
        setTimeout(() => router.push("/home"), 1500);
      } else {
        setErrorMsg(renderMessage(loginRes.data.message || "Login failed."));
      }
    } catch (err: unknown) {
      const msg = axios.isAxiosError(err)
        ? err.response?.data?.detail || `Server Error: ${err.response?.status}`
        : err instanceof Error
        ? err.message
        : "Login request failed";
      setErrorMsg(renderMessage(msg));
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
        {/* Logo with increased margin */}
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
            {" "}
            {/* Increased spacing */}
            <div className="space-y-3">
              {" "}
              {/* Container with spacing */}
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
            {/* Status Messages Area */}
            <div className="h-6 text-center text-sm pt-2 pb-3">
              {" "}
              {/* Added padding */}
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
            {/* Submit Button */}
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
                         transition-all duration-200 ease-out mt-4" /* Enhanced button */
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
            >
              {isLoading ? (
                <>
                  <ArrowPathIcon className="animate-spin h-5 w-5 mr-2.5" />{" "}
                  {/* Larger icon */}
                  Signing In...
                </>
              ) : (
                "Sign In"
              )}
            </motion.button>
          </form>
        </motion.div>

        {/* Sign Up Link Box */}
        <motion.div
          className="w-full mt-8 border border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center bg-gray-50 dark:bg-gray-800/50" // Increased margin and padding
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
