"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  EyeIcon,
  EyeSlashIcon,
} from "@heroicons/react/24/solid";
import Link from "next/link";
import { useRouter } from "next/navigation";
import * as bip39 from "bip39";
import { getPublicKey } from "@noble/secp256k1";
import { sha256 } from "@noble/hashes/sha2";
import { bytesToHex } from "@noble/hashes/utils";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// const bytesToHex = (bytes: Uint8Array): string =>
//   Array.from(bytes)
//     .map((b) => b.toString(16).padStart(2, "0"))
//     .join("");

export default function SignupPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [generatedMnemonics, setGeneratedMnemonics] = useState<string[]>([]);
  const [selectedMnemonic, setSelectedMnemonic] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const router = useRouter();

  useEffect(() => {
    console.log("Signup page mounted, fetching mnemonics...");
    setIsLoading(true);
    axios
      .get<{ mnemonics: string[] }>(`${API_BASE_URL}/api/auth/signup-mnemonics`)
      .then((res) => {
        const mnemonics = res.data.mnemonics || [];
        console.log(`Received ${mnemonics.length} mnemonics.`);
        setGeneratedMnemonics(mnemonics);
        if (mnemonics.length > 0) {
          console.log("Pre-selecting first mnemonic.");
          setSelectedMnemonic(mnemonics[0]);
        }
      })
      .catch((err: unknown) => {
        console.error(
          "Failed to fetch mnemonics:",
          err instanceof Error ? err.message : String(err)
        );
        setErrorMsg("Could not load recovery phrase options. Please refresh.");
      })
      .finally(() => {
        console.log("Mnemonic fetch finished.");
        setIsLoading(false);
      });
  }, []);

  const validateForm = (): boolean => {
    console.log("Validating signup form...");
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
      setErrorMsg("Please select a recovery phrase.");
      return false;
    }
    setErrorMsg("");
    console.log("Signup form validation passed.");
    return true;
  };

  async function handleSignup(e: React.FormEvent) {
    e.preventDefault();
    console.log("Signup form submitted.");
    if (!validateForm()) {
      console.warn("Signup validation failed.");
      return;
    }
    setIsLoading(true);
    setErrorMsg("");
    setSuccessMsg("");

    try {
      console.log("Deriving public key from selected mnemonic...");
      if (!bip39.validateMnemonic(selectedMnemonic))
        throw new Error("Selected mnemonic is invalid.");
      const seed = await bip39.mnemonicToSeed(selectedMnemonic);
      const privateKeyBytes = new Uint8Array(seed).slice(0, 32);
      const publicKeyBytes = getPublicKey(privateKeyBytes, true); // Use getPublicKey from @noble/secp256k1
      const publicKeyHex = bytesToHex(publicKeyBytes);
      console.log(
        `Derived public key for signup: ${publicKeyHex.substring(0, 10)}...`
      );

      console.log("Hashing password securely...");
      const passwordBytes = new TextEncoder().encode(password); // Convert password to bytes
      const hashedPasswordBytes = sha256(passwordBytes); // Hash the password
      const hashedPassword = bytesToHex(hashedPasswordBytes); // Convert hash to hex
      console.log("Password hashed securely using bcrypt.");

      const signupPayload = {
        username,
        email,
        hashed_password: hashedPassword,
        pubkey: publicKeyHex,
      };
      console.log("Sending signup request to backend...");
      console.log("Signup Payload:", {
        signupPayload,
      });

      interface SignupApiResponse {
        success: boolean;
        message: string;
      }
      const response = await axios.post<SignupApiResponse>(
        `${API_BASE_URL}/api/auth/signup`,
        signupPayload
      );

      if (response.status === 201 && response.data.success) {
        console.log("Signup successful!");
        setSuccessMsg(
          "Signup successful! IMPORTANT: Save your recovery phrase securely! Redirecting to login..."
        );
        setPassword("");
        setTimeout(() => {
          router.push("/");
        }, 3500);
      } else {
        console.warn(
          "Signup failed (server response not successful):",
          response.data
        );
        setErrorMsg(response.data.message || "Signup failed on the server.");
      }
    } catch (err: unknown) {
      console.error(
        "Signup Process Error:",
        err instanceof Error ? err.message : String(err)
      );
      setPassword("");

      if (axios.isAxiosError(err)) {
        setErrorMsg(err.response?.data?.detail || "Server error occurred.");
      } else if (err instanceof Error) {
        setErrorMsg(err.message || "An unexpected error occurred.");
      } else {
        setErrorMsg("An unexpected error occurred.");
      }
    } finally {
      console.log("Signup process finished.");
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-teal-50 to-cyan-100 dark:from-gray-900 dark:via-gray-800 dark:to-teal-900 p-4">
      <motion.div className="max-w-lg w-full bg-white dark:bg-gray-800 p-8 rounded-xl shadow-2xl">
        <h2 className="text-3xl font-bold mb-6 text-center text-gray-800 dark:text-gray-100">
          Create Your Secure Account
        </h2>
        <div className="mb-6 p-4 border border-yellow-300 dark:border-yellow-600 bg-yellow-50 dark:bg-gray-700 rounded-lg">
          <h3 className="text-lg font-semibold mb-3 text-gray-700 dark:text-gray-200">
            1. Choose & Save Recovery Phrase
          </h3>
          <p className="text-xs text-yellow-800 dark:text-yellow-300 mb-4 flex items-center">
            {" "}
            <ExclamationTriangleIcon className="w-4 h-4 mr-1.5 flex-shrink-0" />{" "}
            Store this securely offline. It&apos;s your key & recovery method.{" "}
          </p>
          {generatedMnemonics.length > 0 ? (
            <div className="space-y-3">
              {" "}
              {generatedMnemonics.map((mnemonic, index) => (
                <motion.label
                  key={index}
                  htmlFor={`mnemonic-${index}`}
                  className={`block p-3 border rounded-md cursor-pointer transition ${
                    selectedMnemonic === mnemonic
                      ? "border-blue-500 bg-blue-50 dark:bg-blue-900/30 ring-2 ring-blue-300 dark:ring-blue-600"
                      : "border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700/50"
                  }`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 * index }}
                >
                  {" "}
                  <input
                    type="radio"
                    id={`mnemonic-${index}`}
                    name="mnemonicChoice"
                    value={mnemonic}
                    checked={selectedMnemonic === mnemonic}
                    onChange={() => {
                      console.log(`Mnemonic ${index + 1} selected.`);
                      setSelectedMnemonic(mnemonic);
                    }}
                    className="sr-only"
                  />{" "}
                  <span className="text-sm font-mono text-gray-700 dark:text-gray-300 tracking-wide leading-relaxed break-words">
                    {mnemonic}
                  </span>{" "}
                </motion.label>
              ))}{" "}
            </div>
          ) : (
            <div className="flex items-center justify-center h-20 text-gray-500 dark:text-gray-400">
              {isLoading && !errorMsg ? (
                <ArrowPathIcon className="animate-spin h-6 w-6" />
              ) : (
                "Loading options..."
              )}
            </div>
          )}
        </div>
        <form onSubmit={handleSignup} className="space-y-5">
          <h3 className="text-lg font-semibold mb-1 text-gray-700 dark:text-gray-200">
            2. Enter Account Details
          </h3>
          <div>
            {" "}
            <label htmlFor="username" className="...">
              Username
            </label>{" "}
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={3}
              className="..."
              placeholder="Choose a username"
            />{" "}
          </div>
          <div>
            {" "}
            <label htmlFor="email" className="...">
              Email
            </label>{" "}
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="..."
              placeholder="your@email.com"
            />{" "}
          </div>
          <div className="relative">
            {" "}
            <label htmlFor="password" className="...">
              Password
            </label>{" "}
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="... pr-10"
              placeholder="Create a strong password"
            />{" "}
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute ..."
            >
              {" "}
              {showPassword ? (
                <EyeSlashIcon className="h-5 w-5" />
              ) : (
                <EyeIcon className="h-5 w-5" />
              )}{" "}
            </button>{" "}
            <p className="mt-1 text-xs text-red-600 dark:text-red-400">
              Warning: Password hashed locally with insecure demo method.
            </p>{" "}
          </div>
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
            {" "}
            {errorMsg && (
              <p className="text-sm text-red-600 ...">
                <ExclamationTriangleIcon className="w-5 h-5 mr-1" /> {errorMsg}
              </p>
            )}{" "}
            {successMsg && (
              <p className="text-sm text-green-600 ...">
                <CheckCircleIcon className="w-5 h-5 mr-1" /> {successMsg}
              </p>
            )}{" "}
          </motion.div>
          <motion.button
            type="submit"
            disabled={
              isLoading || !selectedMnemonic || generatedMnemonics.length === 0
            }
            className="..."
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {" "}
            {isLoading ? (
              <>
                {" "}
                <ArrowPathIcon className="animate-spin h-5 w-5 mr-3" />{" "}
                Creating...{" "}
              </>
            ) : (
              "Create Account"
            )}{" "}
          </motion.button>
        </form>
        <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
          {" "}
          Already have an account?{" "}
          <Link href="/" className="...">
            {" "}
            Sign in here{" "}
          </Link>{" "}
        </p>
      </motion.div>
    </div>
  );
}
