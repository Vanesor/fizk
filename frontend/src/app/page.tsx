"use client";

import { useState, useEffect } from "react"; // Removed useCallback
import axios from "axios";
import { motion } from "framer-motion";
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  // LockClosedIcon, // Removed unused icon
  EyeIcon,
  EyeSlashIcon,
  KeyIcon,
} from "@heroicons/react/24/solid";
import Link from "next/link";
import { useRouter } from "next/navigation";
import * as bip39 from "bip39";
import { ec as EC } from "elliptic";
import { sha256 } from "@noble/hashes/sha2";
import { bytesToHex } from "@noble/hashes/utils"; // Import bytesToHex directly
import { getPublicKey } from "@noble/secp256k1";
import Particles, { initParticlesEngine } from "@tsparticles/react"; // Correct import
import { loadSlim } from "@tsparticles/slim";
import type { Container, Engine } from "@tsparticles/engine"; // Import types
import { particlesOptions } from "@/config/particlesConfig";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
const ec = new EC("secp256k1");

// --- Helper Functions ---
const hexToBytes = (hex: string): Uint8Array => {
  // ... (function remains the same)
  if (hex.length % 2 !== 0) throw new Error("Invalid hex string length.");
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substring(i, i + 2), 16);
  }
  return bytes;
};

// bytesToHex is imported directly from @noble/hashes/utils now

const renderMessage = (msg: unknown) => {
  // ... (function remains the same)
  if (typeof msg === "string") return msg;
  try {
    return JSON.stringify(msg);
  } catch {
    return String(msg);
  }
};
// --- End Helper Functions ---

export default function LoginPage() {
  const [init, setInit] = useState(false);
  const [mnemonicInput, setMnemonicInput] = useState("");
  const [isMnemonicVisible, setIsMnemonicVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const router = useRouter();

  // Initialize particles engine
  useEffect(() => {
    initParticlesEngine(async (engine: Engine) => {
      await loadSlim(engine);
    }).then(() => {
      setInit(true);
    });
  }, []);

  // Correct prop name is 'particlesLoaded', add Container type
  const particlesInit = async (container?: Container): Promise<void> => {
    console.log("Particles container loaded", container);
  };

  async function handleLogin(e: React.FormEvent) {
    // ... (logic remains the same)
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
      setMnemonicInput(""); // Clear input on error
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
      setMnemonicInput(""); // Clear input on error
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

    setMnemonicInput(""); // Clear mnemonic after successful signing

    try {
      const loginRes = await axios.post(`${API_BASE_URL}/api/auth/login`, {
        pubkey: publicKeyHex,
        signature_der: signatureDER,
        challengeHex: challengeHex,
      });
      if (loginRes.data.success) {
        setSuccessMsg(`Authentication successful! Welcome back.`);
        // Optionally store token/session info here
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
    return null; // Or a loading spinner
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden py-12">
      <Particles
        id="tsparticles-signup"
        particlesLoaded={particlesInit} // Use particlesLoaded prop
        options={particlesOptions}
        className="absolute inset-0 z-0"
      />
      <motion.div
        className="relative z-10 max-w-md w-full bg-gray-900/80 backdrop-blur-sm p-8 rounded-xl shadow-2xl border border-gray-700"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex justify-center mb-6">
          <KeyIcon className="h-12 w-12 text-cyan-400" />
        </div>
        <h2 className="text-3xl font-bold mb-2 text-center text-gray-100">
          Secure Authentication
        </h2>
        <p className="text-center text-sm text-gray-400 mb-6">
          Sign in using your recovery phrase.
        </p>
        <form onSubmit={handleLogin} className="space-y-6">
          {/* Mnemonic Input Section */}
          <div className="p-4 border border-cyan-700/50 bg-gray-800/60 rounded-lg shadow-inner">
            <label
              htmlFor="mnemonic"
              className="block text-sm font-medium text-cyan-300 mb-2"
            >
              Enter Your 12-Word Recovery Phrase
            </label>
            <p className="text-xs text-gray-400 mb-3 flex items-start">
              <ExclamationTriangleIcon className="w-4 h-4 mr-1.5 mt-0.5 flex-shrink-0 text-yellow-400" />
              Used locally to sign the login challenge. Never sent to the
              server.
            </p>
            <div className="relative">
              <textarea
                id="mnemonic"
                rows={3}
                value={mnemonicInput}
                onChange={(e) => setMnemonicInput(e.target.value)}
                className={`w-full p-3 border rounded-md shadow-sm focus:ring-cyan-500 focus:border-cyan-500 bg-gray-700 text-gray-100 transition placeholder-gray-500 border-gray-600 font-mono text-sm tracking-wider ${
                  isMnemonicVisible ? "" : "blur-sm"
                }`}
                placeholder="Enter phrase here..."
                spellCheck="false"
                required
                readOnly={isLoading}
                style={{ filter: isMnemonicVisible ? "none" : "blur(5px)" }}
              />
              <button
                type="button"
                onClick={() => setIsMnemonicVisible(!isMnemonicVisible)}
                className="absolute top-2 right-2 p-1.5 text-gray-400 hover:text-cyan-300 rounded-full bg-gray-800/50 hover:bg-gray-700/70 transition"
                aria-label={isMnemonicVisible ? "Hide phrase" : "Show phrase"}
              >
                {isMnemonicVisible ? (
                  <EyeSlashIcon className="h-5 w-5" />
                ) : (
                  <EyeIcon className="h-5 w-5" />
                )}
              </button>
            </div>
          </div>

          {/* Status Message Area */}
          <motion.div
            className="h-6 text-center"
            initial={false}
            animate={
              errorMsg || successMsg
                ? { opacity: 1, y: 0 }
                : { opacity: 0, y: -10 }
            }
            transition={{ duration: 0.3 }}
          >
            {errorMsg && (
              <p className="text-sm text-red-400 flex items-center justify-center">
                <ExclamationTriangleIcon className="w-5 h-5 mr-1.5" />{" "}
                {renderMessage(errorMsg)}
              </p>
            )}
            {successMsg && (
              <p className="text-sm text-green-400 flex items-center justify-center">
                <CheckCircleIcon className="w-5 h-5 mr-1.5" />{" "}
                {renderMessage(successMsg)}
              </p>
            )}
          </motion.div>

          {/* Submit Button */}
          <motion.button
            type="submit"
            disabled={isLoading || !mnemonicInput}
            className="w-full flex justify-center items-center bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 px-4 border border-transparent rounded-md shadow-lg text-base font-semibold focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 focus:ring-offset-gray-900 transition duration-150 ease-in-out"
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.99 }}
          >
            {isLoading ? (
              // Fix: Wrap adjacent JSX elements in a fragment
              <>
                <ArrowPathIcon className="animate-spin h-5 w-5 mr-3" />{" "}
                Authenticating...
              </>
            ) : (
              "Sign In Securely"
            )}
          </motion.button>
        </form>

        {/* Link to Signup - Fix: Ensure <p> tag is correctly placed */}
        <p className="mt-8 text-center text-sm text-gray-400">
          Don&apos;t have an account?{" "}
          <Link
            href="/signup"
            className="font-medium text-cyan-400 hover:text-cyan-300 transition duration-150 ease-in-out hover:underline"
          >
            Create one here
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
