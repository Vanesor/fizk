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
    console.log("LoginPage: useEffect started");

    const safetyTimeout = setTimeout(() => {
      if (isMounted && !init) {
        console.warn("LoginPage: Safety timeout triggered - forcing init");
        setInit(true);
      }
    }, 5000);

    const initialize = async () => {
      try {
        console.log("LoginPage: Starting particles initialization");
        setInit(true);
        if (!particlesInitialized) {
          await initParticlesEngine(async (engine) => {
            await loadSlim(engine);
          });
          if (isMounted) {
            setParticlesInitialized(true);
          }
        }
      } catch (err) {
        console.error("LoginPage: Error in initialization:", err);
      }
    };

    initialize();

    return () => {
      isMounted = false;
      clearTimeout(safetyTimeout);
    };
  }, []);

  const particlesInit = async (container?: Container): Promise<void> => {
    console.log("Particles container loaded", container);
  };

  const ParticlesBackground = useMemo(() => {
    return (
      <Particles
        id="tsparticles-login"
        particlesLoaded={particlesInit}
        options={particlesOptions}
        className="absolute inset-0 z-0"
      />
    );
  }, []);

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
        setSuccessMsg(`Authentication successful! Welcome back.`);
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
    return <LoadingScreen message="Initializing Secure Environment..." />;
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-gray-900 via-[#0a1025] to-[#111827] p-4">
      <div
        className="absolute inset-0 z-0 bg-gradient-radial from-transparent via-transparent to-black opacity-70"
        style={{
          background:
            "radial-gradient(circle at center, rgba(6,8,24,0) 0%, rgba(6,8,24,0.5) 70%, rgba(2,4,10,0.95) 100%)",
        }}
      ></div>
      {ParticlesBackground}

      <motion.div
        className="relative z-10 w-full max-w-md bg-gray-900/70 backdrop-blur-lg rounded-xl shadow-2xl border border-gray-700/50 overflow-hidden"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        <div className="p-8 md:p-10">
          {" "}
          <div className="flex flex-col items-center mb-8">
            <div className="relative mb-4">
              <div className="absolute -inset-2 rounded-full bg-cyan-500/10 blur-lg"></div>
              <KeyIcon className="relative h-12 w-12 text-cyan-400" />
            </div>
            <h2 className="text-2xl font-semibold text-center text-gray-100">
              Secure Sign In
            </h2>
            <p className="text-center text-sm text-gray-400 mt-2">
              Use your recovery phrase to access your account.
            </p>
          </div>
          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label
                htmlFor="mnemonic"
                className="block text-sm font-medium text-gray-300 mb-2"
              >
                Recovery Phrase (12 Words)
              </label>
              <div className="relative">
                <textarea
                  id="mnemonic"
                  rows={3}
                  value={mnemonicInput}
                  onChange={(e) => setMnemonicInput(e.target.value)}
                  className={`block w-full p-3 border rounded-md shadow-sm focus:ring-cyan-500 focus:border-cyan-500 bg-gray-800 text-gray-100 transition placeholder-gray-500 border-gray-600 font-mono text-sm resize-none ${
                    isMnemonicVisible ? "" : "blur-[4px]"
                  }`}
                  placeholder="Enter your 12-word phrase..."
                  spellCheck="false"
                  required
                  readOnly={isLoading}
                  style={{ filter: isMnemonicVisible ? "none" : "blur(4px)" }}
                />
                <button
                  type="button"
                  onClick={() => setIsMnemonicVisible(!isMnemonicVisible)}
                  className="absolute top-2 right-2 p-1.5 text-gray-400 hover:text-cyan-300 rounded-full bg-gray-700/50 hover:bg-gray-600/70 transition-colors duration-200"
                  aria-label={isMnemonicVisible ? "Hide phrase" : "Show phrase"}
                >
                  {isMnemonicVisible ? (
                    <EyeSlashIcon className="h-5 w-5" />
                  ) : (
                    <EyeIcon className="h-5 w-5" />
                  )}
                </button>
              </div>
              <p className="mt-2 text-xs text-gray-400 flex items-start">
                <ExclamationTriangleIcon className="w-3.5 h-3.5 mr-1.5 mt-0.5 flex-shrink-0 text-amber-400" />
                Phrase is used locally to sign in, never sent to the server.
              </p>
            </div>

            <motion.div
              className="h-5 text-center text-sm"
              initial={false}
              animate={
                errorMsg || successMsg
                  ? { opacity: 1, y: 0, height: "auto" }
                  : { opacity: 0, y: -5, height: "1.25rem" }
              }
              transition={{ duration: 0.3 }}
            >
              {errorMsg && (
                <p className="text-red-400 flex items-center justify-center">
                  <ExclamationTriangleIcon className="w-4 h-4 mr-1.5" />
                  {renderMessage(errorMsg)}
                </p>
              )}
              {successMsg && (
                <p className="text-green-400 flex items-center justify-center">
                  <CheckCircleIcon className="w-4 h-4 mr-1.5" />
                  {renderMessage(successMsg)}
                </p>
              )}
            </motion.div>

            <motion.button
              type="submit"
              disabled={isLoading || !mnemonicInput}
              className="w-full flex justify-center items-center bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-60 disabled:cursor-not-allowed text-white py-2.5 px-4 border border-transparent rounded-md shadow-md text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 focus:ring-offset-gray-900 transition-all duration-200 ease-out"
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.99 }}
            >
              {isLoading ? (
                <>
                  <ArrowPathIcon className="animate-spin h-4 w-4 mr-2" />
                  Authenticating...
                </>
              ) : (
                "Sign In Securely"
              )}
            </motion.button>
          </form>
          <div className="mt-8 text-center">
            <div className="relative my-4">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-700"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-gray-900/70 text-gray-500">
                  New User?
                </span>
              </div>
            </div>
            <p className="text-sm text-gray-400">
              <Link
                href="/signup"
                className="font-medium text-cyan-400 hover:text-cyan-300 hover:underline transition duration-150 ease-in-out"
              >
                Create an account
              </Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
