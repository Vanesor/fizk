"use client";

import { useState, useEffect, useMemo } from "react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  EyeIcon,
  EyeSlashIcon,
  UserPlusIcon,
  ClipboardDocumentIcon,
  LockClosedIcon,
  ChevronRightIcon,
} from "@heroicons/react/24/solid";
import Link from "next/link";
import { useRouter } from "next/navigation";
import * as bip39 from "bip39";
import { sha256 } from "@noble/hashes/sha2";
import { bytesToHex } from "@noble/hashes/utils";
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
  const [currentStep, setCurrentStep] = useState(1);
  const [seedInput, setSeedInput] = useState("");
  const [isSeedVisible, setIsSeedVisible] = useState(false);
  const [seedType, setSeedType] = useState<"provided" | "custom">("provided");
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
        id="tsparticles-signup"
        particlesLoaded={particlesInit}
        options={particlesOptions}
        className="absolute inset-0 z-0"
      />
    ),
    []
  );

  useEffect(() => {
    setIsFetchingMnemonics(true);
    axios
      .get<{ mnemonics: string[] }>(`${API_BASE_URL}/api/auth/signup-mnemonics`)
      .then((res) => {
        const mnemonics = res.data.mnemonics || [];
        setGeneratedMnemonics(mnemonics);
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

  const validateCurrentStep = (): boolean => {
    setErrorMsg("");
    if (currentStep === 1) {
      if (seedType === "provided" && !selectedMnemonic) {
        setErrorMsg("Please select a recovery phrase.");
        return false;
      }

      if (seedType === "custom") {
        const { isValidHex } = validateSeed(seedInput);
        if (!isValidHex) {
          setErrorMsg("Please enter a valid 64-character hex seed.");
          return false;
        }
      }
    } else if (currentStep === 2) {
      if (!username.trim() || username.length < 3) {
        setErrorMsg("Username must be at least 3 characters.");
        return false;
      }
      if (!email.trim() || !EMAIL_REGEX.test(email)) {
        setErrorMsg("Please enter a valid email address.");
        return false;
      }
      if (!password || password.length < 8) {
        setErrorMsg("Password must be at least 8 characters.");
        return false;
      }
    }
    return true;
  };

  const handleNextStep = () => {
    if (validateCurrentStep()) {
      setCurrentStep(currentStep + 1);
    }
  };
  const handlePrevStep = () => {
    setCurrentStep(currentStep - 1);
  };

  const validateForm = (): boolean => {
    setErrorMsg("");

    if (seedType === "provided") {
      if (!selectedMnemonic) {
        setErrorMsg("Recovery phrase not selected.");
        return false;
      }
    } else {
      const { isValidHex } = validateSeed(seedInput);
      if (!isValidHex) {
        setErrorMsg("Please enter a valid 64-character hex seed.");
        return false;
      }
    }

    if (!username.trim() || username.length < 3) {
      setErrorMsg("Username must be at least 3 characters.");
      return false;
    }
    if (!email.trim() || !EMAIL_REGEX.test(email)) {
      setErrorMsg("Please enter a valid email address.");
      return false;
    }
    if (!password || password.length < 8) {
      setErrorMsg("Password must be at least 8 characters.");
      return false;
    }
    return true;
  };

  async function handleSignup(e: React.FormEvent) {
    e.preventDefault();
    if (!validateForm()) return;
    setIsLoading(true);
    setErrorMsg("");
    setSuccessMsg("");

    try {
      const seedToUse =
        seedType === "provided" ? selectedMnemonic : formatSeed(seedInput);

      if (seedType === "provided" && !bip39.validateMnemonic(seedToUse)) {
        throw new Error("Selected recovery phrase is invalid.");
      }

      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { privateKey, publicKey } = await SchnorrAuth.deriveKeyPair(
        seedToUse,
        password
      );
      const passwordBytes = new TextEncoder().encode(password);
      const hashedPasswordBytes = sha256(passwordBytes);
      const hashedPassword = bytesToHex(hashedPasswordBytes);

      const signupPayload = {
        username,
        email,
        hashed_password: hashedPassword,
        pubkey: publicKey,
      };

      const response = await axios.post<{ success: boolean; message: string }>(
        `${API_BASE_URL}/api/auth/signup`,
        signupPayload
      );
      if (response.status === 201 && response.data.success) {
        setSuccessMsg("Account created! Redirecting to login...");
        setPassword("");
        setTimeout(() => {
          router.push("/");
        }, 2500);
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

  const stepIndicator = (
    stepNum: number,
    label: string,
    Icon: React.ElementType
  ) => (
    <div
      className={`flex items-center transition-colors duration-300 ${
        currentStep === stepNum
          ? "text-blue-600 dark:text-blue-400"
          : "text-gray-500 dark:text-gray-400"
      }`}
    >
      <div
        className={`flex items-center justify-center h-8 w-8 rounded-full mr-2.5 transition-colors duration-300 ${
          currentStep === stepNum
            ? "bg-blue-100 dark:bg-blue-900/30"
            : currentStep > stepNum
            ? "bg-green-100 dark:bg-green-900/30"
            : "bg-gray-100 dark:bg-gray-700/50"
        }`}
      >
        <Icon
          className={`h-4 w-4 transition-colors duration-300 ${
            currentStep > stepNum ? "text-green-600 dark:text-green-400" : ""
          }`}
        />
      </div>
      <span
        className={`text-sm font-medium ${
          currentStep === stepNum ? "font-semibold" : ""
        }`}
      >
        {label}
      </span>
    </div>
  );

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-gray-900 to-gray-800 p-6 font-sans">
      {ParticlesBackground}
      <div className="absolute inset-0 bg-black/40 z-0"></div>

      <div className="relative z-10 w-full max-w-lg flex flex-col items-center">
        <div className="mb-10 flex items-center justify-center">
          <div className="p-4 bg-blue-500/10 rounded-full">
            <UserPlusIcon className="h-12 w-12 text-blue-400" />
          </div>
        </div>

        <motion.div
          className="w-full bg-gray-50 dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700"
          initial={{ opacity: 0, y: -15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        >
          <div className="p-8 md:p-10 border-b border-gray-200 dark:border-gray-700">
            <h1 className="text-2xl font-semibold text-center text-gray-900 dark:text-white mb-8">
              Create your account
            </h1>
            <div className="flex items-center justify-center space-x-8">
              {stepIndicator(1, "Recovery Phrase", LockClosedIcon)}
              <div className="w-12 h-0.5 bg-gray-300 dark:bg-gray-600 relative">
                <div
                  className={`absolute inset-0 bg-blue-500 transition-all duration-500 ${
                    currentStep > 1 ? "w-full" : "w-0"
                  }`}
                ></div>
              </div>
              {stepIndicator(2, "Account Details", UserPlusIcon)}
            </div>
          </div>

          <div className="p-8 md:p-10">
            <AnimatePresence mode="wait">
              {currentStep === 1 && (
                <motion.div
                  key="step1"
                  initial={{ opacity: 0, x: -15 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 15 }}
                  transition={{ duration: 0.25, ease: "easeInOut" }}
                  className="space-y-8"
                >
                  <div className="flex items-start p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-700/30">
                    <ExclamationTriangleIcon className="w-6 h-6 mt-0.5 mr-3.5 flex-shrink-0 text-yellow-600 dark:text-yellow-400" />{" "}
                    <div className="space-y-1.5">
                      <p className="font-semibold text-sm text-yellow-800 dark:text-yellow-300">
                        Important Security Information
                      </p>
                      <p className="text-xs text-yellow-700 dark:text-yellow-200 leading-relaxed">
                        {seedType === "provided"
                          ? "Write down this 12-word phrase and store it securely offline. This is the ONLY way to recover your account. Never share it."
                          : "Keep your custom seed secure and backed up. This is the ONLY way to recover your account."}
                      </p>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <legend className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Recovery Method:
                      </legend>
                    </div>

                    <SeedTypeToggle
                      seedType={seedType === "provided" ? "mnemonic" : "custom"}
                      setSeedType={(type) =>
                        setSeedType(type === "mnemonic" ? "provided" : "custom")
                      }
                    />

                    {seedType === "provided" ? (
                      <fieldset className="space-y-4">
                        <legend className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 px-1">
                          Select your recovery phrase:
                        </legend>

                        {isFetchingMnemonics ? (
                          <div className="flex flex-col items-center justify-center h-40 text-gray-500 dark:text-gray-400">
                            <ArrowPathIcon className="animate-spin h-6 w-6 mb-3" />
                            <p>Loading recovery phrases...</p>
                          </div>
                        ) : (
                          <div className="space-y-4">
                            {generatedMnemonics.map((mnemonic, index) => (
                              <label
                                key={index}
                                htmlFor={`mnemonic-${index}`}
                                className={`relative flex items-center p-4 border rounded-lg cursor-pointer transition-all duration-200 
                                           ${
                                             selectedMnemonic === mnemonic
                                               ? "border-blue-500 bg-blue-50 dark:bg-blue-900/30 ring-2 ring-blue-500/40 shadow-md"
                                               : "border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700/30 hover:border-gray-400 dark:hover:border-gray-500 hover:shadow-sm"
                                           }`}
                              >
                                <input
                                  type="radio"
                                  id={`mnemonic-${index}`}
                                  name="mnemonicChoice"
                                  value={mnemonic}
                                  checked={selectedMnemonic === mnemonic}
                                  onChange={() => setSelectedMnemonic(mnemonic)}
                                  className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500 mr-4"
                                />
                                <span className="text-sm font-mono text-gray-800 dark:text-gray-200 tracking-wide leading-relaxed break-words flex-grow">
                                  {mnemonic}
                                </span>
                                <button
                                  type="button"
                                  onClick={(e) => {
                                    e.preventDefault();
                                    handleCopyToClipboard(mnemonic, index);
                                  }}
                                  className="ml-4 flex-shrink-0 p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 rounded-md bg-gray-200/70 dark:bg-gray-600/70 hover:bg-gray-300/80 dark:hover:bg-gray-500/80 transition-colors duration-150"
                                  aria-label="Copy phrase"
                                >
                                  {copiedIndex === index ? (
                                    <CheckCircleIcon className="h-5 w-5 text-green-500" />
                                  ) : (
                                    <ClipboardDocumentIcon className="h-5 w-5" />
                                  )}
                                </button>
                              </label>
                            ))}
                          </div>
                        )}
                      </fieldset>
                    ) : (
                      <div className="space-y-4">
                        <CustomSeedInfoBox />

                        <div className="space-y-2">
                          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                            Enter your custom seed:
                          </label>

                          <SeedInput
                            seed={seedInput}
                            setSeed={setSeedInput}
                            isSeedVisible={isSeedVisible}
                            setIsSeedVisible={setIsSeedVisible}
                          />

                          {seedInput.trim() && (
                            <div className="mt-2">
                              <SeedValidator seed={seedInput} />
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="flex justify-end mt-6">
                    <motion.button
                      type="button"
                      onClick={handleNextStep}
                      className="flex items-center justify-center py-2.5 px-5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg shadow-md transition-colors"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      Continue
                      <ChevronRightIcon className="h-4 w-4 ml-2" />
                    </motion.button>
                  </div>
                </motion.div>
              )}
              {currentStep === 2 && (
                <motion.form
                  key="step2"
                  initial={{ opacity: 0, x: 15 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -15 }}
                  transition={{ duration: 0.25, ease: "easeInOut" }}
                  onSubmit={handleSignup}
                  className="space-y-6"
                >
                  <div className="space-y-6">
                    <div className="space-y-1.5">
                      <label
                        htmlFor="username"
                        className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
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
                        className="block w-full p-3.5 border rounded-lg shadow-sm 
                                  bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100 
                                  placeholder-gray-400 dark:placeholder-gray-500 
                                  border-gray-300 dark:border-gray-600 text-sm transition-all duration-200
                                  hover:border-gray-400 dark:hover:border-gray-500
                                  focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 focus:ring-opacity-50 dark:focus:border-blue-400 dark:focus:ring-blue-400/20"
                        placeholder="Choose a username"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label
                        htmlFor="email"
                        className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
                      >
                        Email Address
                      </label>
                      <input
                        id="email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        className="block w-full p-3.5 border rounded-lg shadow-sm 
                                  bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100 
                                  placeholder-gray-400 dark:placeholder-gray-500 
                                  border-gray-300 dark:border-gray-600 text-sm transition-all duration-200
                                  hover:border-gray-400 dark:hover:border-gray-500
                                  focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 focus:ring-opacity-50 dark:focus:border-blue-400 dark:focus:ring-blue-400/20"
                        placeholder="your@email.com"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label
                        htmlFor="password"
                        className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
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
                          className="block w-full p-3.5 border rounded-lg shadow-sm 
                                    bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100 
                                    placeholder-gray-400 dark:placeholder-gray-500 
                                    border-gray-300 dark:border-gray-600 text-sm pr-12 transition-all duration-200
                                    hover:border-gray-400 dark:hover:border-gray-500
                                    focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 focus:ring-opacity-50 dark:focus:border-blue-400 dark:focus:ring-blue-400/20"
                          placeholder="Create a strong password (min. 8 characters)"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-3 bottom-1/2 -translate-y-1/2 p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 rounded-md transition-colors duration-150"
                          aria-label={
                            showPassword ? "Hide password" : "Show password"
                          }
                        >
                          {showPassword ? (
                            <EyeSlashIcon className="h-5 w-5" />
                          ) : (
                            <EyeIcon className="h-5 w-5" />
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                  <div className="h-6 text-center text-sm py-2">
                    {errorMsg && currentStep === 2 && (
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
                  <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-5 pt-4">
                    <motion.button
                      type="button"
                      onClick={handlePrevStep}
                      className="w-full sm:w-1/3 flex justify-center items-center 
                                border border-gray-300 dark:border-gray-600
                                bg-transparent hover:bg-gray-100 dark:hover:bg-gray-700/50
                                text-gray-700 dark:text-gray-300
                                py-4 px-5 rounded-lg shadow-sm 
                                text-base font-medium 
                                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400 dark:focus:ring-offset-gray-800 
                                transition-colors duration-200"
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      Back
                    </motion.button>
                    <motion.button
                      type="submit"
                      disabled={isLoading}
                      className="w-full sm:w-2/3 flex justify-center items-center 
                                bg-gradient-to-r from-blue-600 to-blue-500
                                hover:from-blue-500 hover:to-blue-400
                                disabled:from-blue-400 disabled:to-blue-300 dark:disabled:from-blue-800 dark:disabled:to-blue-700
                                disabled:opacity-70 disabled:cursor-not-allowed 
                                text-white py-4 px-5 rounded-lg shadow-lg
                                text-base font-medium 
                                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-offset-gray-800 
                                transition-all duration-200 ease-out"
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      {isLoading ? (
                        <>
                          <ArrowPathIcon className="animate-spin h-5 w-5 mr-2.5" />{" "}
                          Creating Account...
                        </>
                      ) : (
                        "Create Account"
                      )}
                    </motion.button>
                  </div>
                </motion.form>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
        <motion.div
          className="w-full mt-8 text-center bg-white/5 backdrop-blur-sm rounded-lg p-6 border border-gray-300/20 dark:border-gray-600/20"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2, ease: "easeOut" }}
        >
          <p className="text-sm text-gray-300">
            Already have an account?{" "}
            <Link
              href="/"
              className="font-medium text-blue-400 hover:text-blue-300 hover:underline transition-colors duration-150"
            >
              Sign in
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
