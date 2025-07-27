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
  EnvelopeIcon,
  LockClosedIcon,
} from "@heroicons/react/24/solid";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Particles, { initParticlesEngine } from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import type { Container } from "@tsparticles/engine";
import { particlesOptions } from "@/config/particlesConfig";
import LoadingScreen from "@/components/LoadingScreen";
import { SchnorrAuth } from "@/utils/schnorr";
import {
  SeedInput,
  SeedValidator,
  SeedTypeToggle,
  CustomSeedInfoBox,
} from "@/components/SeedPhraseTools";
import { validateSeed, formatSeed } from "@/utils/seedUtils";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

const renderMessage = (msg: unknown) => {
  if (typeof msg === "string") return msg;
  try {
    return JSON.stringify(msg);
  } catch {
    return String(msg);
  }
};

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function LoginPage() {
  const [init, setInit] = useState(false);
  const [particlesInitialized, setParticlesInitialized] = useState(false);
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [seedInput, setSeedInput] = useState("");
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const [isSeedVisible, setIsSeedVisible] = useState(false);
  const [seedType, setSeedType] = useState<"mnemonic" | "custom">("mnemonic");
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

  const isFormValid = () => {
    if (
      identifier.trim() === "" ||
      password.trim() === "" ||
      seedInput.trim() === ""
    ) {
      return false;
    }

    const { isValidMnemonic, isValidHex } = validateSeed(seedInput);

    if (seedType === "mnemonic") {
      return isValidMnemonic;
    } else {
      return isValidHex;
    }
  };

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();

    if (!isFormValid()) {
      setErrorMsg("Please fill in all fields with valid information");
      return;
    }

    setIsLoading(true);
    setErrorMsg("");
    setSuccessMsg("");

    try {
      console.group("🔒 Login Process");
      console.log("Starting Enhanced Schnorr ZKP authentication...");

      const isEmail = EMAIL_REGEX.test(identifier);
      console.log(
        `🔍 Using ${
          isEmail ? "email" : "username"
        } as identifier: ${identifier}`
      );

      console.log("🔄 Resolving identifier to public key...");
      const userResponse = await fetch(
        `${API_BASE_URL}/api/auth/resolve-user`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            identifier: identifier,
            is_email: isEmail,
          }),
        }
      );

      if (!userResponse.ok) {
        const error = await userResponse.json();
        throw new Error(error.detail || "Invalid credentials");
      }

      const { pubkey } = await userResponse.json();
      console.log(
        `✅ Identifier resolved to public key: ${pubkey.substring(0, 16)}...`
      );

      const formattedSeed = formatSeed(seedInput);

      console.log("🔑 Deriving key pair from seed + password...");
      const { privateKey, publicKey } = await SchnorrAuth.deriveKeyPair(
        formattedSeed,
        password
      );

      if (publicKey !== pubkey) {
        console.error("❌ Derived public key doesn't match stored key");
        throw new Error("Invalid seed or password combination");
      }

      const result = await SchnorrAuth.authenticate(
        API_BASE_URL,
        privateKey,
        publicKey
      );

      setSuccessMsg(
        `Welcome back, ${result.username || identifier}! Redirecting...`
      );
      console.log("✅ Authentication successful! Redirecting...");
      console.groupEnd();

      if (result.token) {
        localStorage.setItem("authToken", result.token);
      }

      setSeedInput("");
      setPassword("");
      setIdentifier("");

      setTimeout(() => router.push("/dashboard"), 1500);
    } catch (err: unknown) {
      console.error("❌ Authentication failed:", err);
      console.groupEnd();

      if (err instanceof Error) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg(
          "Authentication failed. Please check your credentials and try again."
        );
      }
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

          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label
                htmlFor="identifier"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Username or Email
              </label>
              <div className="relative mt-1">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <EnvelopeIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="identifier"
                  type="text"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  className="block w-full pl-10 pr-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  placeholder="Email or username"
                  required
                  readOnly={isLoading}
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Password
              </label>
              <div className="relative mt-1">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <LockClosedIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="password"
                  type={isPasswordVisible ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-10 pr-10 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  placeholder="••••••••"
                  required
                  readOnly={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setIsPasswordVisible(!isPasswordVisible)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
                  aria-label={
                    isPasswordVisible ? "Hide password" : "Show password"
                  }
                >
                  {isPasswordVisible ? (
                    <EyeSlashIcon className="h-5 w-5" />
                  ) : (
                    <EyeIcon className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>

            <div>
              <label
                htmlFor="seed"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Recovery Method
              </label>

              <SeedTypeToggle seedType={seedType} setSeedType={setSeedType} />

              {seedType === "custom" && <CustomSeedInfoBox />}

              <div className="mt-3">
                <SeedInput
                  seed={seedInput}
                  setSeed={setSeedInput}
                  isSeedVisible={isSeedVisible}
                  setIsSeedVisible={setIsSeedVisible}
                  readOnly={isLoading}
                />
              </div>

              <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                {seedType === "mnemonic"
                  ? "Enter your 12-word recovery phrase, separated by spaces."
                  : "Enter your 64-character hex seed generated with our tool."}
              </p>

              {seedInput.trim() && (
                <div className="mt-2">
                  <SeedValidator seed={seedInput.trim()} />
                </div>
              )}
            </div>

            <div className="h-6 text-center text-sm">
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
              disabled={isLoading || !isFormValid()}
              className="w-full flex justify-center items-center 
                         bg-gradient-to-r from-blue-600 to-blue-500
                         hover:from-blue-500 hover:to-blue-400 
                         disabled:from-blue-400 disabled:to-blue-300 dark:disabled:from-blue-800 dark:disabled:to-blue-700 
                         disabled:opacity-70 disabled:cursor-not-allowed 
                         text-white py-3 px-4 rounded-lg shadow-lg 
                         text-base font-medium 
                         focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-offset-gray-800 
                         transition-all duration-200 ease-out"
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
            >
              {isLoading ? (
                <>
                  <ArrowPathIcon className="animate-spin h-5 w-5 mr-2.5" />
                  Authenticating...
                </>
              ) : (
                "Sign In"
              )}
            </motion.button>

            <div className="text-center mt-4">
              <Link
                href="/forgot-password"
                className="text-sm text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
              >
                Forgot your password or recovery phrase?
              </Link>
            </div>
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
