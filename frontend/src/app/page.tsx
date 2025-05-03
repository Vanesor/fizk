"use client";

import { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  LockClosedIcon,
  EyeIcon,
  EyeSlashIcon,
} from "@heroicons/react/24/solid";
import Link from "next/link";
import { useRouter } from "next/navigation";
import * as bip39 from "bip39";
import { ec as EC } from "elliptic";
import { sha256 } from "@noble/hashes/sha2";
import { getPublicKey } from "@noble/secp256k1";

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

const bytesToHex = (bytes: Uint8Array): string =>
  Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");

const renderMessage = (msg: unknown) => {
  if (typeof msg === "string") return msg;
  try {
    return JSON.stringify(msg);
  } catch {
    return String(msg);
  }
};

export default function LoginPage() {
  const [mnemonicInput, setMnemonicInput] = useState("");
  const [isMnemonicVisible, setIsMnemonicVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const router = useRouter();

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
        throw new Error("Invalid mnemonic.");
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
        throw new Error("Invalid challenge.");
    } catch (err: unknown) {
      const msg = axios.isAxiosError(err)
        ? err.response?.data?.detail || err.message
        : err instanceof Error
        ? err.message
        : err;
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
      setErrorMsg(err instanceof Error ? err.message : renderMessage(err));
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
        setSuccessMsg(`Welcome back, ${loginRes.data.username}!`);
        setTimeout(() => router.push("/home"), 1500);
      } else {
        setErrorMsg(renderMessage(loginRes.data.message));
      }
    } catch (err: unknown) {
      const msg = axios.isAxiosError(err)
        ? err.response?.data?.detail || err.message
        : err instanceof Error
        ? err.message
        : err;
      setErrorMsg(renderMessage(msg));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-100 dark:from-gray-900 dark:via-gray-800 dark:to-indigo-900 p-4">
      <motion.div
        className="max-w-md w-full bg-white dark:bg-gray-800 p-8 rounded-xl shadow-2xl"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex justify-center mb-6">
          <LockClosedIcon className="h-12 w-12 text-blue-600 dark:text-blue-400" />
        </div>
        <h2 className="text-3xl font-bold mb-2 text-center text-gray-800 dark:text-gray-100">
          Secure Sign In
        </h2>
        <p className="text-center text-sm text-gray-500 dark:text-gray-400 mb-6">
          Authenticate using your recovery phrase.
        </p>
        <form onSubmit={handleLogin} className="space-y-6">
          <div className="p-4 border border-red-300 dark:border-red-600 bg-red-50 dark:bg-gray-700/50 rounded-lg">
            <label
              htmlFor="mnemonic"
              className="block text-sm font-medium text-red-700 dark:text-red-300 mb-2"
            >
              Enter Your 12-Word Recovery Phrase
            </label>
            <p className="text-xs text-red-600 dark:text-red-400 mb-3 flex items-start">
              <ExclamationTriangleIcon className="w-4 h-4 mr-1.5 mt-0.5 flex-shrink-0" />{" "}
              Only used locally to sign the login challenge.
            </p>
            <div className="relative">
              <textarea
                id="mnemonic"
                rows={3}
                value={mnemonicInput}
                onChange={(e) => setMnemonicInput(e.target.value)}
                className={`w-full p-3 border rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-gray-100 transition placeholder-gray-400 dark:placeholder-gray-500 ${
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
                className="absolute top-2 right-2 p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 rounded-full bg-white/50 dark:bg-gray-800/50"
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
              <p className="text-sm text-red-600 dark:text-red-400 flex items-center justify-center">
                <ExclamationTriangleIcon className="w-5 h-5 mr-1" />{" "}
                {renderMessage(errorMsg)}
              </p>
            )}
            {successMsg && (
              <p className="text-sm text-green-600 dark:text-green-400 flex items-center justify-center">
                <CheckCircleIcon className="w-5 h-5 mr-1" />{" "}
                {renderMessage(successMsg)}
              </p>
            )}
          </motion.div>
          <motion.button
            type="submit"
            disabled={isLoading || !mnemonicInput}
            className="w-full flex justify-center items-center bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white py-3 px-4 border border-transparent rounded-md shadow-sm text-base font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-offset-gray-800 transition duration-150 ease-in-out"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isLoading ? (
              <>
                <ArrowPathIcon className="animate-spin h-5 w-5 mr-3" /> Signing
                In...
              </>
            ) : (
              "Sign In Securely"
            )}
          </motion.button>
        </form>
        <p className="mt-8 text-center text-sm text-gray-600 dark:text-gray-400">
          Don&apos;t have an account?{" "}
          <Link
            href="/signup"
            className="font-medium text-green-600 hover:text-green-500 dark:text-green-400 dark:hover:text-green-300 transition duration-150 ease-in-out"
          >
            Create one here
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
