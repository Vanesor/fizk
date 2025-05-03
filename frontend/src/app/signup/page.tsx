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
  UserPlusIcon,
  ClipboardDocumentIcon,
} from "@heroicons/react/24/solid";
import Link from "next/link";
import { useRouter } from "next/navigation";
import * as bip39 from "bip39";
import { getPublicKey } from "@noble/secp256k1";
import { sha256 } from "@noble/hashes/sha2";
import { bytesToHex } from "@noble/hashes/utils";
import Particles, { initParticlesEngine } from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import type { Container } from "@tsparticles/engine";
import { particlesOptions } from "@/config/particlesConfig";
import LoadingScreen from "@/components/LoadingScreen";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const renderMessage = (msg: unknown) => {
  if (typeof msg === "string") return msg;
  try {
    return JSON.stringify(msg);
  } catch {
    return String(msg);
  }
};

export default function SignupPage() {
  const [init, setInit] = useState(false);
  const [particlesInitialized, setParticlesInitialized] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [generatedMnemonics, setGeneratedMnemonics] = useState<string[]>([]);
  const [selectedMnemonic, setSelectedMnemonic] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [isFetchingMnemonics, setIsFetchingMnemonics] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const router = useRouter();

  useEffect(() => {
    let isMounted = true;
    console.log("SignupPage: useEffect started.");

    // Safety timeout - will ensure loading screen disappears after 5 seconds
    const safetyTimeout = setTimeout(() => {
      if (isMounted && !init) {
        console.warn("SignupPage: Safety timeout triggered - forcing init");
        setInit(true);
      }
    }, 5000);

    const initialize = async () => {
      try {
        console.log("SignupPage: Starting particles initialization");
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
        console.error("SignupPage: Error in initialization:", err);
      }
    };

    initialize();

    return () => {
      console.log("SignupPage: useEffect cleanup - component unmounted.");
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
        id="tsparticles-signup"
        particlesLoaded={particlesInit}
        options={particlesOptions}
        className="absolute inset-0 z-0"
      />
    );
  }, []);

  useEffect(() => {
    setIsFetchingMnemonics(true);
    axios
      .get<{ mnemonics: string[] }>(`${API_BASE_URL}/api/auth/signup-mnemonics`)
      .then((res) => {
        const mnemonics = res.data.mnemonics || [];
        setGeneratedMnemonics(mnemonics);
        if (mnemonics.length > 0) {
          setSelectedMnemonic(mnemonics[0]);
        }
      })
      .catch((err: unknown) => {
        console.error("Failed to fetch mnemonics:", err);
        setErrorMsg("Could not load recovery phrase options. Please refresh.");
      })
      .finally(() => {
        setIsFetchingMnemonics(false);
      });
  }, []);

  const handleCopyToClipboard = (mnemonic: string, index: number) => {
    navigator.clipboard.writeText(mnemonic).then(() => {
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    });
  };

  const validateForm = (): boolean => {
    if (!username.trim() || username.length < 3) {
      setErrorMsg("Username must be at least 3 characters long.");
      return false;
    }
    if (!email.trim() || !EMAIL_REGEX.test(email)) {
      setErrorMsg("Please enter a valid email address.");
      return false;
    }
    if (!password || password.length < 8) {
      setErrorMsg("Password must be at least 8 characters long.");
      return false;
    }
    if (!selectedMnemonic) {
      setErrorMsg("Please select or generate a recovery phrase.");
      return false;
    }
    setErrorMsg("");
    return true;
  };

  async function handleSignup(e: React.FormEvent) {
    e.preventDefault();
    if (!validateForm()) return;
    setIsLoading(true);
    setErrorMsg("");
    setSuccessMsg("");

    try {
      if (!bip39.validateMnemonic(selectedMnemonic))
        throw new Error("Selected recovery phrase is invalid.");

      const seed = await bip39.mnemonicToSeed(selectedMnemonic);
      const privateKeyBytes = new Uint8Array(seed).slice(0, 32);
      const publicKeyBytes = getPublicKey(privateKeyBytes, true);
      const publicKeyHex = bytesToHex(publicKeyBytes);
      const passwordBytes = new TextEncoder().encode(password);
      const hashedPasswordBytes = sha256(passwordBytes);
      const hashedPassword = bytesToHex(hashedPasswordBytes);

      const signupPayload = {
        username,
        email,
        hashed_password: hashedPassword,
        pubkey: publicKeyHex,
      };

      const response = await axios.post<{ success: boolean; message: string }>(
        `${API_BASE_URL}/api/auth/signup`,
        signupPayload
      );

      if (response.status === 201 && response.data.success) {
        setSuccessMsg(
          "Signup successful! IMPORTANT: Ensure you saved your recovery phrase! Redirecting..."
        );
        setPassword("");
        setTimeout(() => {
          router.push("/");
        }, 3500);
      } else {
        setErrorMsg(response.data.message || "Signup failed on the server.");
      }
    } catch (err: unknown) {
      setPassword("");
      if (axios.isAxiosError(err)) {
        setErrorMsg(
          err.response?.data?.detail || "An error occurred during signup."
        );
      } else if (err instanceof Error) {
        setErrorMsg(err.message || "An unexpected error occurred.");
      } else {
        setErrorMsg("An unexpected error occurred.");
      }
    } finally {
      setIsLoading(false);
    }
  }

  if (!init) {
    return <LoadingScreen message="Preparing Signup..." />;
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-gray-900 via-[#0a1829] to-[#111827] py-10 px-4">
      <div
        className="absolute inset-0 z-0 bg-gradient-radial from-transparent via-transparent to-black opacity-70"
        style={{
          background:
            "radial-gradient(circle at center, rgba(6,8,24,0) 0%, rgba(4,10,24,0.5) 70%, rgba(2,6,12,0.95) 100%)",
        }}
      ></div>
      {ParticlesBackground}

      <motion.div
        className="relative z-10 w-full max-w-2xl bg-gray-900/70 backdrop-blur-lg rounded-xl shadow-2xl border border-gray-700/50 overflow-hidden"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        <div className="p-8 md:p-10">
          {" "}
          <div className="flex flex-col items-center mb-8">
            <div className="relative mb-4">
              <div className="absolute -inset-2 rounded-full bg-teal-500/10 blur-lg"></div>
              <UserPlusIcon className="relative h-12 w-12 text-teal-400" />
            </div>
            <h2 className="text-2xl font-semibold text-center text-gray-100">
              Create Account
            </h2>
            <p className="text-center text-sm text-gray-400 mt-2">
              Secure your account with a recovery phrase.
            </p>
          </div>
          <div className="mb-8 space-y-4">
            <h3 className="text-base font-semibold text-teal-300 flex items-center">
              <span className="flex items-center justify-center w-5 h-5 rounded-full bg-teal-800 text-teal-300 mr-2.5 text-xs font-bold">
                1
              </span>
              Choose & Save Recovery Phrase
            </h3>
            <p className="pl-7 text-xs text-gray-400 flex items-start">
              <ExclamationTriangleIcon className="w-3.5 h-3.5 mr-1.5 mt-0.5 flex-shrink-0 text-amber-400" />
              <span>
                <span className="font-semibold text-amber-300">CRITICAL:</span>{" "}
                Store this phrase securely offline. It&apos;s your only recovery
                method.
              </span>
            </p>
            {isFetchingMnemonics ? (
              <div className="flex items-center justify-center h-24 text-gray-400 text-sm">
                <ArrowPathIcon className="animate-spin h-5 w-5 mr-2 text-teal-500/70" />
                Loading phrase options...
              </div>
            ) : generatedMnemonics.length > 0 ? (
              <div className="space-y-3 pl-7">
                {generatedMnemonics.map((mnemonic, index) => (
                  <motion.label
                    key={index}
                    htmlFor={`mnemonic-${index}`}
                    className={`relative block p-3 pr-10 border rounded-md cursor-pointer transition-colors duration-200 ${
                      selectedMnemonic === mnemonic
                        ? "border-teal-600 bg-teal-900/30 ring-1 ring-teal-600/50"
                        : "border-gray-600 hover:bg-gray-700/40"
                    }`}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.05 * index }}
                  >
                    <input
                      type="radio"
                      id={`mnemonic-${index}`}
                      name="mnemonicChoice"
                      value={mnemonic}
                      checked={selectedMnemonic === mnemonic}
                      onChange={() => setSelectedMnemonic(mnemonic)}
                      className="sr-only"
                    />
                    <span className="text-xs font-mono text-gray-300 tracking-wider leading-relaxed break-words">
                      {mnemonic}
                    </span>
                    <button
                      type="button"
                      onClick={() => handleCopyToClipboard(mnemonic, index)}
                      className="absolute top-1/2 right-2 transform -translate-y-1/2 p-1 text-gray-400 hover:text-teal-300 rounded-md bg-gray-700/50 hover:bg-gray-600/70 transition-colors duration-200"
                      aria-label="Copy phrase"
                    >
                      {copiedIndex === index ? (
                        <CheckCircleIcon className="h-4 w-4 text-green-400" />
                      ) : (
                        <ClipboardDocumentIcon className="h-4 w-4" />
                      )}
                    </button>
                  </motion.label>
                ))}
              </div>
            ) : (
              <div className="pl-7 text-sm text-red-400 bg-red-900/20 border border-red-800/30 rounded-md p-3 flex items-center justify-center">
                <ExclamationTriangleIcon className="h-4 w-4 mr-2" />
                Failed to load recovery phrases. Please refresh.
              </div>
            )}
          </div>
          <form onSubmit={handleSignup} className="space-y-5">
            <h3 className="text-base font-semibold text-teal-300 flex items-center">
              <span className="flex items-center justify-center w-5 h-5 rounded-full bg-teal-800 text-teal-300 mr-2.5 text-xs font-bold">
                2
              </span>
              Enter Account Details
            </h3>
            <div className="grid gap-4 md:grid-cols-2 pl-7">
              <div>
                <label
                  htmlFor="username"
                  className="block text-xs font-medium text-gray-300 mb-1.5"
                >
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  minLength={3}
                  className="block w-full p-2.5 border rounded-md shadow-sm focus:ring-teal-500 focus:border-teal-500 bg-gray-800 text-gray-100 text-sm border-gray-600 placeholder-gray-500"
                  placeholder="Choose a username"
                />
              </div>
              <div>
                <label
                  htmlFor="email"
                  className="block text-xs font-medium text-gray-300 mb-1.5"
                >
                  Email Address
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="block w-full p-2.5 border rounded-md shadow-sm focus:ring-teal-500 focus:border-teal-500 bg-gray-800 text-gray-100 text-sm border-gray-600 placeholder-gray-500"
                  placeholder="your@email.com"
                />
              </div>
              <div className="relative md:col-span-2">
                <label
                  htmlFor="password"
                  className="block text-xs font-medium text-gray-300 mb-1.5"
                >
                  Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    minLength={8}
                    className="block w-full p-2.5 border rounded-md shadow-sm focus:ring-teal-500 focus:border-teal-500 bg-gray-800 text-gray-100 text-sm border-gray-600 placeholder-gray-500 pr-10"
                    placeholder="Create a strong password (min. 8 characters)"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 flex items-center px-3 text-gray-400 hover:text-teal-300"
                    aria-label={
                      showPassword ? "Hide password" : "Show password"
                    }
                  >
                    {showPassword ? (
                      <EyeSlashIcon className="h-4 w-4" />
                    ) : (
                      <EyeIcon className="h-4 w-4" />
                    )}
                  </button>
                </div>
                <p className="mt-1.5 text-xs text-amber-400/90 flex items-center">
                  <ExclamationTriangleIcon className="w-3.5 h-3.5 mr-1.5 flex-shrink-0" />
                  Warning: Password hashed locally (insecure demo).
                </p>
              </div>
            </div>

            <motion.div
              className="h-5 text-center text-sm pl-7"
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
                <p className="text-green-400 flex items-center justify-center text-center">
                  <CheckCircleIcon className="w-4 h-4 mr-1.5 flex-shrink-0" />
                  {renderMessage(successMsg)}
                </p>
              )}
            </motion.div>

            <div className="pl-7 pt-2">
              <motion.button
                type="submit"
                disabled={isLoading || isFetchingMnemonics || !selectedMnemonic}
                className="w-full flex justify-center items-center bg-gradient-to-r from-teal-600 to-cyan-600 hover:from-teal-500 hover:to-cyan-500 disabled:opacity-60 disabled:cursor-not-allowed text-white py-2.5 px-4 border border-transparent rounded-md shadow-md text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500 focus:ring-offset-gray-900 transition-all duration-200 ease-out"
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.99 }}
              >
                {isLoading ? (
                  <>
                    <ArrowPathIcon className="animate-spin h-4 w-4 mr-2" />
                    Creating Account...
                  </>
                ) : (
                  "Create Account"
                )}
              </motion.button>
            </div>
          </form>
          <div className="mt-8 text-center">
            <div className="relative my-4">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-700"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-gray-900/70 text-gray-500">
                  Already Registered?
                </span>
              </div>
            </div>
            <p className="text-sm text-gray-400">
              <Link
                href="/"
                className="font-medium text-teal-400 hover:text-teal-300 hover:underline transition duration-150 ease-in-out"
              >
                Sign in here
              </Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
