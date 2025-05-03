"use client";

import { useState, useEffect } from "react"; // Removed useCallback
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
import { bytesToHex } from "@noble/hashes/utils"; // Import bytesToHex directly
import Particles, { initParticlesEngine } from "@tsparticles/react"; // Correct import
import { loadSlim } from "@tsparticles/slim";
import type { Container, Engine } from "@tsparticles/engine"; // Import types
import { particlesOptions } from "@/config/particlesConfig";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// --- Helper Function (renderMessage) ---
const renderMessage = (msg: unknown) => {
  // ... (function remains the same)
  if (typeof msg === "string") return msg;
  try {
    return JSON.stringify(msg);
  } catch {
    return String(msg);
  }
};
// --- End Helper Function ---

export default function SignupPage() {
  const [init, setInit] = useState(false);
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

  // Initialize particles engine
  useEffect(() => {
    initParticlesEngine(async (engine: Engine) => {
      // Add Engine type
      await loadSlim(engine);
    }).then(() => {
      setInit(true);
    });
  }, []);

  // Correct prop name is 'particlesLoaded', add Container type
  const particlesInit = async (container?: Container): Promise<void> => {
    console.log("Particles container loaded", container);
  };

  // Fetch Mnemonics
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
        // Log or use the error
        console.error("Failed to fetch mnemonics:", err);
        setErrorMsg("Could not load recovery phrase options. Please refresh.");
      })
      .finally(() => {
        setIsFetchingMnemonics(false);
      });
  }, []);

  const handleCopyToClipboard = (mnemonic: string, index: number) => {
    // ... (function remains the same)
    navigator.clipboard.writeText(mnemonic).then(() => {
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000); // Reset after 2 seconds
    });
  };

  const validateForm = (): boolean => {
    // ... (function remains the same)
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
    // ... (logic remains the same)
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

      // WARNING: Client-side hashing like this is NOT secure for production.
      // Use a proper backend hashing mechanism (like bcrypt, Argon2).
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
        setPassword(""); // Clear password field
        setTimeout(() => {
          router.push("/"); // Redirect to login
        }, 3500);
      } else {
        setErrorMsg(response.data.message || "Signup failed on the server.");
      }
    } catch (err: unknown) {
      setPassword(""); // Clear password field on error
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
    return null; // Or a loading spinner
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
      <Particles
        id="tsparticles"
        particlesLoaded={particlesInit} // Use particlesLoaded prop
        options={particlesOptions}
        className="absolute inset-0 z-0"
      />
      <motion.div
        className="relative z-10 max-w-2xl w-full bg-gray-900/80 backdrop-blur-sm p-8 rounded-xl shadow-2xl border border-gray-700"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex justify-center mb-6">
          <UserPlusIcon className="h-12 w-12 text-teal-400" />
        </div>
        <h2 className="text-3xl font-bold mb-6 text-center text-gray-100">
          Create Your Secure Account
        </h2>

        {/* Step 1: Mnemonic Selection */}
        <div className="mb-8 p-5 border border-teal-700/50 bg-gray-800/60 rounded-lg shadow-inner">
          <h3 className="text-lg font-semibold mb-3 text-teal-300">
            1. Choose & Save Your Recovery Phrase
          </h3>
          <p className="text-xs text-gray-400 mb-4 flex items-start">
            <ExclamationTriangleIcon className="w-4 h-4 mr-1.5 mt-0.5 flex-shrink-0 text-yellow-400" />
            <span className="font-semibold mr-1">CRITICAL:</span> Store this
            phrase securely offline. It&apos;s your only way to recover your
            account.
          </p>
          {isFetchingMnemonics ? (
            <div className="flex items-center justify-center h-24 text-gray-400">
              <ArrowPathIcon className="animate-spin h-6 w-6 mr-2" /> Loading
              phrase options...
            </div>
          ) : generatedMnemonics.length > 0 ? (
            <div className="space-y-3">
              {generatedMnemonics.map((mnemonic, index) => (
                <motion.label
                  key={index}
                  htmlFor={`mnemonic-${index}`}
                  className={`relative block p-3 pr-10 border rounded-md cursor-pointer transition ${
                    selectedMnemonic === mnemonic
                      ? "border-teal-500 bg-teal-900/30 ring-2 ring-teal-600"
                      : "border-gray-600 hover:bg-gray-700/50"
                  }`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 * index }}
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
                  <span className="text-sm font-mono text-gray-300 tracking-wide leading-relaxed break-words">
                    {mnemonic}
                  </span>
                  <button
                    type="button"
                    onClick={() => handleCopyToClipboard(mnemonic, index)}
                    className="absolute top-1/2 right-2 transform -translate-y-1/2 p-1.5 text-gray-400 hover:text-teal-300 rounded-md bg-gray-700/50 hover:bg-gray-600/70 transition"
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
            <p className="text-center text-red-400">
              Failed to load recovery phrases.
            </p>
          )}
        </div>

        {/* Step 2: Account Details Form */}
        <form onSubmit={handleSignup} className="space-y-5">
          <h3 className="text-lg font-semibold mb-3 text-teal-300">
            2. Enter Account Details
          </h3>
          {/* Username Input */}
          <div>
            <label
              htmlFor="username"
              className="block text-sm font-medium text-gray-300 mb-1"
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
              className="w-full p-2.5 border rounded-md shadow-sm focus:ring-teal-500 focus:border-teal-500 bg-gray-700 text-gray-100 border-gray-600 placeholder-gray-500"
              placeholder="Choose a unique username"
            />
          </div>
          {/* Email Input */}
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-300 mb-1"
            >
              Email Address
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full p-2.5 border rounded-md shadow-sm focus:ring-teal-500 focus:border-teal-500 bg-gray-700 text-gray-100 border-gray-600 placeholder-gray-500"
              placeholder="your@email.com"
            />
          </div>
          {/* Password Input */}
          <div className="relative">
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-300 mb-1"
            >
              Password
            </label>
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="w-full p-2.5 border rounded-md shadow-sm focus:ring-teal-500 focus:border-teal-500 bg-gray-700 text-gray-100 border-gray-600 placeholder-gray-500 pr-10"
              placeholder="Create a strong password"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 top-6 flex items-center pr-3 text-gray-400 hover:text-teal-300" // Adjusted top margin
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? (
                <EyeSlashIcon className="h-5 w-5" />
              ) : (
                <EyeIcon className="h-5 w-5" />
              )}
            </button>
            <p className="mt-1.5 text-xs text-yellow-400 flex items-center">
              <ExclamationTriangleIcon className="w-3 h-3 mr-1 flex-shrink-0" />
              Warning: Password hashed locally (insecure demo).
            </p>
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
              <p className="text-sm text-green-400 flex items-center justify-center text-center">
                <CheckCircleIcon className="w-5 h-5 mr-1.5 flex-shrink-0" />{" "}
                {renderMessage(successMsg)}
              </p>
            )}
          </motion.div>

          {/* Submit Button */}
          <motion.button
            type="submit"
            disabled={isLoading || isFetchingMnemonics || !selectedMnemonic}
            className="w-full flex justify-center items-center bg-gradient-to-r from-teal-500 to-cyan-600 hover:from-teal-600 hover:to-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 px-4 border border-transparent rounded-md shadow-lg text-base font-semibold focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500 focus:ring-offset-gray-900 transition duration-150 ease-in-out"
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.99 }}
          >
            {isLoading ? (
              <>
                <ArrowPathIcon className="animate-spin h-5 w-5 mr-3" /> Creating
                Account...
              </>
            ) : (
              "Create Account"
            )}
          </motion.button>
        </form>

        {/* Link to Login */}
        <p className="mt-8 text-center text-sm text-gray-400">
          Already have an account?{" "}
          <Link
            href="/"
            className="font-medium text-teal-400 hover:text-teal-300 transition duration-150 ease-in-out hover:underline"
          >
            Sign in here
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
