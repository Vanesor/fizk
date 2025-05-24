import React from "react";
import { motion } from "framer-motion";
import {
  CheckCircleIcon,
  XMarkIcon,
  ArrowDownTrayIcon,
  InformationCircleIcon,
  EyeIcon,
  EyeSlashIcon,
} from "@heroicons/react/24/solid";
import { downloadSeedGenerator } from "@/utils/downloadUtils";
import { validateSeed } from "@/utils/seedUtils";

interface SeedInputProps {
  seed: string;
  setSeed: (seed: string) => void;
  isSeedVisible: boolean;
  setIsSeedVisible: (visible: boolean) => void;
  readOnly?: boolean;
  className?: string;
}

export const SeedInput: React.FC<SeedInputProps> = ({
  seed,
  setSeed,
  isSeedVisible,
  setIsSeedVisible,
  readOnly = false,
  className = "",
}) => {
  return (
    <div className={`relative ${className}`}>
      <textarea
        value={seed}
        onChange={(e) => setSeed(e.target.value)}
        rows={3}
        className={`block w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm 
                 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100 
                 font-mono text-sm resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                 ${isSeedVisible ? "" : "filter blur-sm"}`}
        placeholder="Enter your recovery phrase or custom seed..."
        spellCheck="false"
        readOnly={readOnly}
      />
      <button
        type="button"
        onClick={() => setIsSeedVisible(!isSeedVisible)}
        className="absolute bottom-2 right-2 p-1.5 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 rounded-md bg-gray-200/50 dark:bg-gray-600/50 hover:bg-gray-300/70 dark:hover:bg-gray-500/70 transition-colors duration-150"
        aria-label={isSeedVisible ? "Hide seed" : "Show seed"}
      >
        {isSeedVisible ? (
          <EyeSlashIcon className="h-5 w-5" />
        ) : (
          <EyeIcon className="h-5 w-5" />
        )}
      </button>
    </div>
  );
};

export const SeedValidator: React.FC<{ seed: string }> = ({ seed }) => {
  const { isValidHex, isValidMnemonic } = validateSeed(seed);

  return (
    <div className="space-y-1.5">
      {/* Valid hex format check */}
      <div className="flex items-center space-x-2">
        {isValidHex ? (
          <CheckCircleIcon className="h-4 w-4 text-green-500" />
        ) : (
          <XMarkIcon className="h-4 w-4 text-red-500" />
        )}
        <span className="text-xs text-gray-600 dark:text-gray-300">
          {isValidHex
            ? "Valid hex seed format (64 characters)"
            : "Not a valid hex seed (must be 64 hex characters)"}
        </span>
      </div>

      {/* Valid BIP39 mnemonic check */}
      <div className="flex items-center space-x-2">
        {isValidMnemonic ? (
          <CheckCircleIcon className="h-4 w-4 text-green-500" />
        ) : (
          <XMarkIcon className="h-4 w-4 text-red-500" />
        )}
        <span className="text-xs text-gray-600 dark:text-gray-300">
          {isValidMnemonic
            ? "Valid BIP39 recovery phrase"
            : "Not a valid BIP39 recovery phrase"}
        </span>
      </div>

      {!isValidHex && !isValidMnemonic && (
        <div className="pt-1 text-xs text-amber-600 dark:text-amber-400">
          Please enter either a valid 12-word recovery phrase or a 64-character
          hex seed
        </div>
      )}
    </div>
  );
};

interface SeedTypeToggleProps {
  seedType: "mnemonic" | "custom"; // Match the state type in page.tsx
  setSeedType: (type: "mnemonic" | "custom") => void; // Match the state setter
}

export const SeedTypeToggle: React.FC<SeedTypeToggleProps> = ({
  seedType,
  setSeedType,
}) => {
  return (
    <div className="flex flex-col sm:flex-row gap-4 my-5 p-4 bg-gray-100/80 dark:bg-gray-700/40 rounded-xl">
      <button
        type="button"
        onClick={() => setSeedType("mnemonic")}
        className={`flex-1 py-3.5 px-5 text-sm font-medium rounded-lg transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-800 ${
          seedType === "mnemonic"
            ? "bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg border-2 border-blue-400 dark:border-blue-400 transform scale-100"
            : "bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
        }`}
      >
        {seedType === "mnemonic" && (
          <span className="absolute inset-0 bg-blue-500/10 dark:bg-blue-400/10 rounded-lg"></span>
        )}
        Use Recovery Phrase
      </button>
      <button
        type="button"
        onClick={() => setSeedType("custom")}
        className={`flex-1 py-3.5 px-5 text-sm font-medium rounded-lg transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-800 ${
          seedType === "custom"
            ? "bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg border-2 border-blue-400 dark:border-blue-400 transform scale-100"
            : "bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
        }`}
      >
        {seedType === "custom" && (
          <span className="absolute inset-0 bg-blue-500/10 dark:bg-blue-400/10 rounded-lg"></span>
        )}
        Use Custom Seed
      </button>
    </div>
  );
};

export const CustomSeedInfoBox: React.FC = () => {
  const handleDownload = () => {
    downloadSeedGenerator();
  };

  return (
    <div className="p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/30 rounded-lg">
      <div className="flex">
        <InformationCircleIcon className="h-5 w-5 text-amber-500 mr-2 flex-shrink-0" />
        <div className="text-xs text-amber-800 dark:text-amber-300 space-y-2">
          <p className="font-medium">Enhanced Privacy: Custom Seed</p>
          <p>
            Generate your own 64-character hex seed offline using our tool. Use
            any words or phrases you choose without being limited to standard
            word lists.
          </p>
          <div className="flex items-center">
            <motion.button
              onClick={handleDownload}
              className="inline-flex items-center px-2.5 py-1.5 text-xs font-medium bg-amber-100 hover:bg-amber-200 dark:bg-amber-800/50 dark:hover:bg-amber-800/80 text-amber-800 dark:text-amber-200 rounded-md transition-colors"
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
            >
              <ArrowDownTrayIcon className="h-3.5 w-3.5 mr-1.5" />
              Download Seed Generator
            </motion.button>
          </div>
        </div>
      </div>
    </div>
  );
};
