# from coincurve import PrivateKey, PublicKeyXOnly
# import hashlib

# # Step 1: Generate a private key (or load from existing)
# private_key = PrivateKey()

# # Step 2: Derive the corresponding x-only public key
# public_key_xonly = private_key.public_key_xonly  # Assuming this attribute exists

# # Step 3: Prepare the message and compute its hash
# message = b"Hello, Schnorr!"
# message_hash = hashlib.sha256(message).digest()  # 32-byte hash

# # Step 4: Sign the message hash using Schnorr
# signature = private_key.sign_schnorr(message_hash)

# # Step 5: Verify the signature
# try:
#     is_valid = public_key_xonly.verify(signature, message_hash)
#     print("Signature is valid:", is_valid)
# except ValueError as e:
#     print("Verification failed:", e)

















// // app/page.tsx
// "use client";

// import { useState } from "react";
// import axios from "axios";
// import { motion } from "framer-motion";
// import {
//   CheckCircleIcon,
//   ExclamationTriangleIcon,
//   ArrowPathIcon,
//   LockClosedIcon,
//   EyeIcon,
//   EyeSlashIcon,
// } from "@heroicons/react/24/solid";
// import Link from "next/link";
// import { useRouter } from "next/navigation";
// import * as bip39 from "bip39";
// import { getPublicKey } from "@noble/secp256k1";
// import { schnorr } from "@noble/curves/secp256k1";
// import { sha256 } from "@noble/hashes/sha2";

// const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

// // --- Crypto Helpers ---
// const hexToBytes = (hex: string): Uint8Array => {
//   if (hex.length % 2 !== 0) throw new Error("Invalid hex string length.");
//   const bytes = new Uint8Array(hex.length / 2);
//   for (let i = 0; i < hex.length; i += 2) {
//     bytes[i / 2] = parseInt(hex.substring(i, i + 2), 16);
//   }
//   return bytes;
// };

// const bytesToHex = (bytes: Uint8Array): string =>
//   Array.from(bytes)
//     .map((b) => b.toString(16).padStart(2, "0"))
//     .join("");

// // --- Component ---
// export default function LoginPage() {
//   const [mnemonicInput, setMnemonicInput] = useState("");
//   const [isMnemonicVisible, setIsMnemonicVisible] = useState(false);
//   const [isLoading, setIsLoading] = useState(false);
//   const [errorMsg, setErrorMsg] = useState("");
//   const [successMsg, setSuccessMsg] = useState("");
//   const router = useRouter();

//   async function handleLogin(e: React.FormEvent) {
//     e.preventDefault();
//     console.log("Login process started.");
//     setIsLoading(true);
//     setErrorMsg("");
//     setSuccessMsg("");

//     let privateKeyBytes: Uint8Array | null = null;
//     let publicKeyHex: string | null = null;

//     // 1. Validate Mnemonic and Derive Keys
//     try {
//       console.log("Validating mnemonic and deriving keys...");
//       const mnemonic = mnemonicInput.trim();
//       if (!bip39.validateMnemonic(mnemonic)) {
//         throw new Error(
//           "Invalid mnemonic phrase. Check spelling and word count (12 words)."
//         );
//       }
//       const seed = await bip39.mnemonicToSeed(mnemonic);
//       privateKeyBytes = new Uint8Array(seed).slice(0, 32); // Use Uint8Array.prototype.slice()
//       const publicKeyBytes = getPublicKey(privateKeyBytes, true); // Use getPublicKey from @noble/secp256k1
//       publicKeyHex = bytesToHex(publicKeyBytes);
//       console.log(`Derived PubKey: ${publicKeyHex.substring(0, 10)}...`);
//     } catch (err: unknown) {
//       const message =
//         err instanceof Error
//           ? err.message
//           : "An unknown error occurred during key derivation.";
//       console.error("Mnemonic/Key Derivation Error:", message);
//       setErrorMsg(message);
//       setIsLoading(false);
//       setMnemonicInput("");
//       privateKeyBytes = null;
//       return;
//     }

//     if (!privateKeyBytes || !publicKeyHex) {
//       console.error("Key derivation failed unexpectedly after validation.");
//       setErrorMsg("Key derivation failed unexpectedly.");
//       setIsLoading(false);
//       setMnemonicInput("");
//       return;
//     }

//     // 2. Get Challenge from Backend
//     try {
//       console.log(
//         `Requesting challenge for pubkey: ${publicKeyHex.substring(0, 10)}...`
//       );
//       const challengeResponse = await axios.post<{ challengeHex: string }>(
//         `${API_BASE_URL}/api/auth/challenge`,
//         { pubkey: publicKeyHex }
//       );
//       const challengeHex: string = challengeResponse.data.challengeHex;
//       console.log(`Received challenge: ${challengeHex.substring(0, 8)}...`);
//       if (!challengeHex || challengeHex.length !== 64)
//         throw new Error("Invalid challenge.");

//       // 3. Hash the Challenge
//       console.log("Hashing received challenge...");
//       const challengeBytes = hexToBytes(challengeHex);
//       const messageHash = sha256(challengeBytes); // Use correct sha256 import
//       console.log(
//         `Hashed challenge (msg to sign): ${bytesToHex(messageHash).substring(
//           0,
//           16
//         )}...`
//       );

//       // 4. Sign the Message Hash using Schnorr
//       console.log("Signing message hash using Schnorr...");
//       const signature = schnorr.sign(messageHash, privateKeyBytes); // Use correct schnorr import
//       const signatureHex = bytesToHex(signature);
//       const r_hex = signatureHex.slice(0, 64);
//       const s_hex = signatureHex.slice(64);
//       console.log(
//         `Generated Schnorr Sig (r: ${r_hex.substring(
//           0,
//           8
//         )}..., s: ${s_hex.substring(0, 8)}...)`
//       );

//       console.log("Clearing mnemonic from state.");
//       setMnemonicInput("");
//       privateKeyBytes = null;

//       // 5. Send Login Request to Backend
//       console.log(`Sending login request to backend...`);
//       const loginPayload = { pubkey: publicKeyHex, r_hex, s_hex, challengeHex };
//       console.log("Login Payload:", {
//         pubkey: loginPayload.pubkey,
//         r_hex: "...",
//         s_hex: "...",
//         challengeHex: "...",
//       });

//       interface LoginApiResponse {
//         success: boolean;
//         message: string;
//         username?: string;
//       }
//       const loginResponse = await axios.post<LoginApiResponse>(
//         `${API_BASE_URL}/api/auth/login`,
//         loginPayload
//       );

//       if (loginResponse.data.success) {
//         const username = loginResponse.data.username || "user";
//         console.log(`Login successful for ${username}!`);
//         setSuccessMsg(
//           `Login successful! Welcome back, ${username}! Redirecting...`
//         );
//         setTimeout(() => {
//           router.push("/home");
//         }, 1500);
//       } else {
//         console.warn(
//           "Login failed (server success=false):",
//           loginResponse.data.message
//         );
//         setErrorMsg(
//           loginResponse.data.message || "Login failed. Server rejected."
//         );
//       }
//     } catch (err: unknown) {
//       console.error("Login Process Error:", err);
//       console.log("Clearing mnemonic from state due to error.");
//       setMnemonicInput("");
//       privateKeyBytes = null;

//       if (axios.isAxiosError(err)) {
//         setErrorMsg(err.response?.data?.detail || "Server error occurred.");
//       } else if (err instanceof Error) {
//         setErrorMsg(err.message || "An unexpected error during login.");
//       } else {
//         setErrorMsg("An unexpected error occurred.");
//       }
//     } finally {
//       console.log("Login process finished.");
//       setIsLoading(false);
//     }
//   }

//   // --- UI Rendering ---
//   return (
//     <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-100 dark:from-gray-900 dark:via-gray-800 dark:to-indigo-900 p-4">
//       <motion.div
//         className="max-w-md w-full bg-white dark:bg-gray-800 p-8 rounded-xl shadow-2xl"
//         initial={{ opacity: 0, scale: 0.9 }}
//         animate={{ opacity: 1, scale: 1 }}
//         transition={{ duration: 0.5 }}
//       >
//         {/* Header */}
//         <div className="flex justify-center mb-6">
//           <LockClosedIcon className="h-12 w-12 text-blue-600 dark:text-blue-400" />
//         </div>
//         <h2 className="text-3xl font-bold mb-2 text-center text-gray-800 dark:text-gray-100">
//           Secure Sign In
//         </h2>
//         <p className="text-center text-sm text-gray-500 dark:text-gray-400 mb-6">
//           Authenticate using your recovery phrase.
//         </p>
//         {/* Login Form */}
//         <form onSubmit={handleLogin} className="space-y-6">
//           {/* Mnemonic Input */}
//           <div className="p-4 border border-red-300 dark:border-red-600 bg-red-50 dark:bg-gray-700/50 rounded-lg">
//             <label
//               htmlFor="mnemonic"
//               className="block text-sm font-medium text-red-700 dark:text-red-300 mb-2"
//             >
//               Enter Your 12-Word Recovery Phrase
//             </label>
//             <p className="text-xs text-red-600 dark:text-red-400 mb-3 flex items-start">
//               <ExclamationTriangleIcon className="w-4 h-4 mr-1.5 mt-0.5 flex-shrink-0" />
//               <span>Only used locally to sign the login challenge.</span>
//             </p>
//             <div className="relative">
//               <textarea
//                 id="mnemonic"
//                 rows={3}
//                 value={mnemonicInput}
//                 onChange={(e) => setMnemonicInput(e.target.value)}
//                 className={`w-full p-3 border rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-gray-100 transition placeholder-gray-400 dark:placeholder-gray-500 ${
//                   isMnemonicVisible ? "" : "blur-sm"
//                 }`}
//                 placeholder="Enter phrase here..."
//                 spellCheck="false"
//                 required
//                 readOnly={isLoading}
//                 style={{ filter: isMnemonicVisible ? "none" : "blur(5px)" }}
//               />
//               <button
//                 type="button"
//                 onClick={() => setIsMnemonicVisible(!isMnemonicVisible)}
//                 className="absolute top-2 right-2 p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 rounded-full bg-white/50 dark:bg-gray-800/50"
//                 aria-label={isMnemonicVisible ? "Hide phrase" : "Show phrase"}
//               >
//                 {isMnemonicVisible ? (
//                   <EyeSlashIcon className="h-5 w-5" />
//                 ) : (
//                   <EyeIcon className="h-5 w-5" />
//                 )}
//               </button>
//             </div>
//           </div>
//           {/* Status Messages */}
//           <motion.div
//             className="h-6 text-center"
//             initial={false}
//             animate={
//               errorMsg || successMsg
//                 ? { opacity: 1, y: 0 }
//                 : { opacity: 0, y: -10 }
//             }
//             transition={{ duration: 0.3 }}
//           >
//             {errorMsg && (
//               <p className="text-sm text-red-600 dark:text-red-400 flex items-center justify-center">
//                 <ExclamationTriangleIcon className="w-5 h-5 mr-1" /> {errorMsg}
//               </p>
//             )}
//             {successMsg && (
//               <p className="text-sm text-green-600 dark:text-green-400 flex items-center justify-center">
//                 <CheckCircleIcon className="w-5 h-5 mr-1" /> {successMsg}
//               </p>
//             )}
//           </motion.div>
//           {/* Submit Button */}
//           <motion.button
//             type="submit"
//             disabled={isLoading || !mnemonicInput}
//             className="w-full flex justify-center items-center bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white py-3 px-4 border border-transparent rounded-md shadow-sm text-base font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-offset-gray-800 transition duration-150 ease-in-out"
//             whileHover={{ scale: 1.02 }}
//             whileTap={{ scale: 0.98 }}
//           >
//             {isLoading ? (
//               <>
//                 <ArrowPathIcon className="animate-spin h-5 w-5 mr-3" /> Signing
//                 In...
//               </>
//             ) : (
//               "Sign In Securely"
//             )}
//           </motion.button>
//         </form>
//         {/* Link to Signup */}
//         <p className="mt-8 text-center text-sm text-gray-600 dark:text-gray-400">
//           Don&apos;t have an account?{" "}
//           <Link
//             href="/signup"
//             className="font-medium text-green-600 hover:text-green-500 dark:text-green-400 dark:hover:text-green-300 transition duration-150 ease-in-out"
//           >
//             Create one here
//           </Link>
//         </p>
//       </motion.div>
//     </div>
//   );
// }

// app/page.tsx
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
import { schnorr } from "@noble/curves/secp256k1";
import { getPublicKey } from "@noble/secp256k1";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

// --- Crypto Helpers ---
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

// Helper to render errors safely
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

    // 1. Derive keys
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

    // 2. Fetch challenge
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

    // 3. Sign challenge
    let r_hex: string;
    let s_hex: string;
    try {
      const challengeBytes = hexToBytes(challengeHex);
      const signature = await schnorr.sign(challengeBytes, privateKeyBytes);
      const sigHex = bytesToHex(signature);
      r_hex = sigHex.slice(0, 64);
      s_hex = sigHex.slice(64);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : renderMessage(err));
      setIsLoading(false);
      return;
    }

    setMnemonicInput("");

    // 4. Login
    try {
      const loginRes = await axios.post(`${API_BASE_URL}/api/auth/login`, {
        pubkey: publicKeyHex,
        r_hex,
        s_hex,
        challengeHex,
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

















# main.py
import os
import secrets
import time
import hashlib
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from loguru import logger
from coincurve import PublicKey
from database import init_db, get_session
from models import User
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing_extensions import Annotated
import re
from mnemonic import Mnemonic
from contextlib import asynccontextmanager
from hashlib import sha256
from ecdsa import ellipticcurve, numbertheory, util
from ecdsa.curves import SECP256k1
from ecdsa.ellipticcurve import Point
from ecdsa.util import number_to_string, string_to_number

ecdsa_curve = SECP256k1
p = ecdsa_curve.curve.p()
n = ecdsa_curve.order
G = ecdsa_curve.generator

# --- Logging Setup ---
logger.add(
    "logs/backend_{time:YYYY-MM-DD}.log", rotation="1 day", retention="7 days", level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}"
)
logger.add( # Console output
    lambda msg: print(msg, end=""), level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{message}</cyan>",
    colorize=True
)

# --- Lifespan for DB Init ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup: Initializing database...")
    try:
        init_db()
    except Exception as e:
        logger.critical(f"Database initialization failed: {e}. Application cannot start.", exc_info=True)
        raise SystemExit(f"Database initialization failed: {e}") from e
    yield
    logger.info("Application shutdown.")

app = FastAPI(title="FL ZKP Auth Backend", lifespan=lifespan)

# --- CORS Middleware ---
origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# --- Challenge Store (In-memory - NOT FOR PRODUCTION) ---
challenge_store: dict[str, tuple[str, float]] = {}
CHALLENGE_TTL = 300  # 5 minutes

# --- Pydantic Models (Validated) ---
class SignupRequest(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=100, strip_whitespace=True)]
    email: EmailStr
    hashed_password: Annotated[str, Field(min_length=64)]  # Expect SHA-256 hex hash
    pubkey: str  # Compressed pubkey hex

class SignupResponse(BaseModel):
    success: bool
    message: str

class ChallengeRequest(BaseModel):
    pubkey: str

    @field_validator('pubkey')
    @classmethod
    def validate_pubkey(cls, v):
        if not re.match(r'^(02|03)[0-9a-fA-F]{64}$', v):
            raise ValueError("Invalid public key format")
        return v

class ChallengeResponse(BaseModel):
    challengeHex: str

class LoginRequest(BaseModel):
    pubkey: str
    r_hex: str
    s_hex: str
    challengeHex: str

    @field_validator('pubkey')
    @classmethod
    def validate_pubkey(cls, v):
        if not re.match(r'^(02|03)[0-9a-fA-F]{64}$', v):
            raise ValueError("Invalid public key format")
        return v

    @field_validator('r_hex', 's_hex', 'challengeHex')
    @classmethod
    def validate_hex(cls, v, info):
        if not re.match(r'^[0-9a-fA-F]{64}$', v):
            raise ValueError(f"Invalid {info.field_name} format")
        return v

class LoginResponse(BaseModel):
    success: bool
    message: str
    username: str | None = None

# --- Helper Function ---
def hash_sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def _lift_x_to_point(x: int, parity: int) -> ellipticcurve.Point:
    # Solve y^2 = x^3 + 7 mod p, then pick the root matching parity
    y2 = (pow(x, 3, p) + 7) % p
    y0 = pow(y2, (p + 1) // 4, p)
    y  = y0 if (y0 & 1) == parity else p - y0
    # Point(curve, x, y)
    return ellipticcurve.Point(ecdsa_curve.curve, x, y)

def verify_schnorr_signature(pubkey_hex: str, signature_hex: str, message: bytes) -> bool:
    raw_pub = bytes.fromhex(pubkey_hex)
    # accept compressed(33) or x-only(32)
    if len(raw_pub) == 33 and raw_pub[0] in (2, 3):
        parity = raw_pub[0] & 1
        x_bytes = raw_pub[1:]
    elif len(raw_pub) == 32:
        parity = 0
        x_bytes = raw_pub
    else:
        raise ValueError("Invalid public key format")
    x = int.from_bytes(x_bytes, 'big')
    if x >= p:
        return False
    P = _lift_x_to_point(x, parity)

    sig = bytes.fromhex(signature_hex)
    if len(sig) != 64:
        return False
    r = int.from_bytes(sig[:32], 'big')
    s = int.from_bytes(sig[32:], 'big')
    if r >= p or s >= n:
        return False

    # compute e = int(hash(r || pubkey_x || message)) mod n
    e_bytes = sha256(r.to_bytes(32, 'big') + x_bytes + message).digest()
    e = int.from_bytes(e_bytes, 'big') % n

    # R = s*G - e*P
    R = s * G + (-e) * P
    if R == ellipticcurve.INFINITY or (R.x() != r):
        return False
    return True

def sign_schnorr(private_key: int, message: bytes) -> str:
    # naive deterministic nonce: hash(priv || msg)
    k_bytes = sha256(private_key.to_bytes(32, 'big') + message).digest()
    k = int.from_bytes(k_bytes, 'big') % n
    if k == 0:
        raise ValueError("Bad nonce")

    R = k * G
    parity = R.y() & 1
    r = R.x()

    # x-only pub key
    P = private_key * G
    px = P.x()

    e_bytes = sha256(r.to_bytes(32, 'big') + px.to_bytes(32, 'big') + message).digest()
    e = int.from_bytes(e_bytes, 'big') % n

    s = (k + e * private_key) % n
    sig = r.to_bytes(32, 'big') + s.to_bytes(32, 'big')
    return sig.hex()

# --- Logging Middleware ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    log_id = secrets.token_hex(4)
    logger.info(f"RID {log_id} --> {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}")
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(f"RID {log_id} <-- {request.method} {request.url.path} - Status: {response.status_code} ({process_time:.2f}ms)")
        return response
    except Exception as e:
        logger.error(f"RID {log_id} !!! {request.method} {request.url.path} - Unhandled Error: {e}", exc_info=True)
        raise e

# --- API Endpoints ---

@app.get("/api/signup-mnemonics", response_model=dict[str, list[str]], tags=["Auth"])
async def get_signup_mnemonics():
    """Generates three unique 12-word BIP39 mnemonics for client-side selection."""
    logger.debug("Generating mnemonics requested.")
    try:
        mnemo = Mnemonic("english")
        mnemonics = [mnemo.generate(strength=128) for _ in range(3)]
        logger.info(f"Generated {len(mnemonics)} mnemonics for signup selection.")
        return {"mnemonics": mnemonics}
    except Exception as e:
        logger.error(f"Error generating mnemonics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate recovery phrase options")

@app.post("/api/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED, tags=["Auth"])
async def signup(req: SignupRequest, session: Session = Depends(get_session)):
    """Registers a new user with data prepared by the client (username, email, hashed_password, pubkey)."""
    logger.info(f"Signup attempt for username='{req.username}', email='{req.email}', pubkey='{req.pubkey[:10]}...'")

    try:
        PublicKey(bytes.fromhex(req.pubkey))
    except Exception:
        logger.warning(f"Signup failed for '{req.username}': Invalid public key format received: '{req.pubkey}'")
        raise HTTPException(status_code=400, detail="Invalid public key format.")

    existing_user = session.exec(
        select(User).where(
            (User.username == req.username) | (User.email == req.email) | (User.pubkey == req.pubkey)
        )
    ).first()

    if existing_user:
        field = "Username"
        if existing_user.email == req.email: field = "Email"
        elif existing_user.pubkey == req.pubkey: field = "Public key identifier"
        logger.warning(f"Signup failed for '{req.username}': Conflict - {field} already exists.")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{field} already registered.")

    new_user = User(
        username=req.username, email=req.email,
        hashed_password=req.hashed_password,
        pubkey=req.pubkey
    )
    session.add(new_user)

    try:
        session.commit()
        session.refresh(new_user)
        logger.success(f"User '{new_user.username}' registered successfully (ID: {new_user.id}).")
        return SignupResponse(success=True, message="Signup successful! You can now log in.")
    except Exception as e:
        session.rollback()
        logger.error(f"Database error during signup commit for '{req.username}': {e}", exc_info=True)
        if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
            logger.warning(f"Signup conflict during commit for '{req.username}' (likely race condition or re-submission).")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account identifier already exists.")
        raise HTTPException(status_code=500, detail="Failed to save user data due to a server error.")

@app.post("/api/auth/challenge", response_model=ChallengeResponse, tags=["Auth"])
async def get_auth_challenge(req: ChallengeRequest, session: Session = Depends(get_session)):
    """Provides a unique challenge for a given public key if the user exists."""
    logger.info(f"Challenge requested for pubkey: '{req.pubkey[:10]}...'")

    user = session.exec(select(User).where(User.pubkey == req.pubkey)).first()
    if not user:
        logger.warning(f"Challenge requested for non-existent pubkey: '{req.pubkey}'")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No account found for this identifier.")

    challenge_bytes = secrets.token_bytes(32)
    challenge_hex = challenge_bytes.hex()
    challenge_store[req.pubkey] = (challenge_hex, time.time())
    logger.info(f"Generated challenge '{challenge_hex[:8]}...' for pubkey '{req.pubkey[:10]}...'")

    current_time = time.time()
    if secrets.randbelow(10) == 0:
        keys_to_delete = [pk for pk, (_, ts) in challenge_store.items() if current_time - ts > CHALLENGE_TTL]
        if keys_to_delete:
            logger.debug(f"Challenge store cleanup: Removing {len(keys_to_delete)} expired challenges.")
            for pk in keys_to_delete:
                try: del challenge_store[pk]
                except KeyError: pass

    return ChallengeResponse(challengeHex=challenge_hex)

@app.post("/api/auth/login", response_model=LoginResponse, tags=["Auth"])
async def login(req: LoginRequest, session: Session = Depends(get_session)):
    """Verifies the Schnorr signature against the stored challenge."""
    logger.info(f"Login attempt for pubkey: '{req.pubkey[:10]}...'")

    challenge_data = challenge_store.pop(req.pubkey, None)
    current_time = time.time()

    if not challenge_data:
        logger.warning(f"Login failed for '{req.pubkey}': No valid challenge found (potentially expired, used, or never issued).")
        raise HTTPException(status_code=400, detail="Login session invalid or expired. Please try initiating login again.")

    stored_challenge_hex, timestamp = challenge_data
    if current_time - timestamp > CHALLENGE_TTL:
        logger.warning(f"Login failed for '{req.pubkey}': Challenge expired (issued at {timestamp}, current {current_time}).")
        raise HTTPException(status_code=400, detail="Login session expired. Please try again.")
    if stored_challenge_hex != req.challengeHex:
        logger.warning(f"Login failed for '{req.pubkey}': Challenge mismatch. Expected='{stored_challenge_hex[:8]}...', got='{req.challengeHex[:8]}...'.")
        raise HTTPException(status_code=400, detail="Login session data mismatch. Please try again.")

    user = session.exec(select(User).where(User.pubkey == req.pubkey)).first()
    if not user:
        logger.error(f"CRITICAL: Login failed for '{req.pubkey}': User not found in DB despite valid challenge!")
        raise HTTPException(status_code=404, detail="User account inconsistency. Please contact support.")

    try:
        # Combine r and s into a single signature
        signature_hex = req.r_hex + req.s_hex

        # Verify the Schnorr signature
        is_valid = verify_schnorr_signature(req.pubkey, signature_hex, bytes.fromhex(req.challengeHex))

    except Exception as e:
        logger.error(f"Schnorr verification internal error for '{user.username}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Signature verification failed internally.")

    if is_valid:
        logger.success(f"Login successful for user '{user.username}' (pubkey: {req.pubkey}).")
        return LoginResponse(success=True, message="Login successful!", username=user.username)
    else:
        logger.warning(f"Login failed for '{user.username}' (pubkey: {req.pubkey}): Invalid Schnorr signature.")
        raise HTTPException(status_code=401, detail="Authentication failed: Invalid signature.")

# --- Root endpoint (optional) ---
@app.get("/", include_in_schema=False)
async def root():
    return {"message": "ZKP Auth Backend is running."}


// working

import os
import secrets
import time
import hashlib
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from loguru import logger
from coincurve import PublicKey
from database import init_db, get_session
from models import User
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing_extensions import Annotated
import re
from mnemonic import Mnemonic
from contextlib import asynccontextmanager
from hashlib import sha256
from ecdsa import ellipticcurve, numbertheory, util, VerifyingKey
from ecdsa.curves import SECP256k1

ecdsa_curve = SECP256k1
p = ecdsa_curve.curve.p()
n = ecdsa_curve.order
G = ecdsa_curve.generator

logger.add(
    "logs/backend_{time:YYYY-MM-DD}.log", rotation="1 day", retention="7 days", level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}"
)
logger.add( 
    lambda msg: print(msg, end=""), level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{message}</cyan>",
    colorize=True
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup: Initializing database...")
    try:
        init_db()
    except Exception as e:
        logger.critical(f"Database initialization failed: {e}. Application cannot start.", exc_info=True)
        raise SystemExit(f"Database initialization failed: {e}") from e
    yield
    logger.info("Application shutdown.")

app = FastAPI(title="FL ZKP Auth Backend", lifespan=lifespan)

origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

challenge_store: dict[str, tuple[str, float]] = {}
CHALLENGE_TTL = 300  

class SignupRequest(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=100, strip_whitespace=True)]
    email: EmailStr
    hashed_password: Annotated[str, Field(min_length=64)]  
    pubkey: str  

class SignupResponse(BaseModel):
    success: bool
    message: str

class ChallengeRequest(BaseModel):
    pubkey: str

    @field_validator('pubkey')
    @classmethod
    def validate_pubkey(cls, v):
        if not re.match(r'^(02|03)[0-9a-fA-F]{64}$', v):
            raise ValueError("Invalid public key format")
        return v

class ChallengeResponse(BaseModel):
    challengeHex: str

class LoginRequest(BaseModel):
    pubkey: str
    signature_der: str  
    challengeHex: str

    @field_validator('pubkey')
    @classmethod
    def validate_pubkey(cls, v):
        if not re.match(r'^(02|03)[0-9a-fA-F]{64}$', v):
            raise ValueError("Invalid public key format")
        return v

    @field_validator('challengeHex')
    @classmethod
    def validate_challenge_hex(cls, v):
        if not re.match(r'^[0-9a-fA-F]{64}$', v):
            raise ValueError("Invalid challenge format")
        return v

class LoginResponse(BaseModel):
    success: bool
    message: str
    username: str | None = None

def hash_sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def sign_schnorr(private_key: int, message: bytes) -> str:
    # naive deterministic nonce: hash(priv || msg)
    k_bytes = sha256(private_key.to_bytes(32, 'big') + message).digest()
    k = int.from_bytes(k_bytes, 'big') % n
    if k == 0:
        raise ValueError("Bad nonce")

    R = k * G
    parity = R.y() & 1
    r = R.x()

    # x-only pub key
    P = private_key * G
    px = P.x()

    e_bytes = sha256(r.to_bytes(32, 'big') + px.to_bytes(32, 'big') + message).digest()
    e = int.from_bytes(e_bytes, 'big') % n

    s = (k + e * private_key) % n
    sig = r.to_bytes(32, 'big') + s.to_bytes(32, 'big')
    return sig.hex()

def verify_ecdsa_signature(pubkey_hex: str, signature_der: str, message: bytes) -> bool:
    """
    Verifies an ECDSA signature in DER format.
    
    :param pubkey_hex: The public key in compressed hex format (33 bytes).
    :param signature_der: The ECDSA signature in DER format (hex string).
    :param message: The original message (bytes) to verify against.
    :return: True if the signature is valid, False otherwise.
    """
    try:
        # Extract the compressed public key
        pubkey_bytes = bytes.fromhex(pubkey_hex)
        if len(pubkey_bytes) != 33 or pubkey_bytes[0] not in (2, 3):
            logger.warning(f"Invalid public key format: {pubkey_hex[:10]}...")
            return False
            
        # Create verifying key from compressed public key - FIXED!
        vk = VerifyingKey.from_string(
            pubkey_bytes, 
            curve=SECP256k1,
            hashfunc=hashlib.sha256,
            validate_point=True
        )
        
        # Convert DER signature from hex to bytes
        signature_bytes = bytes.fromhex(signature_der)
        
        # Hash the message using SHA-256
        msg_hash = hash_sha256(message)
        
        # Verify the signature
        return vk.verify_digest(signature_bytes, msg_hash, sigdecode=util.sigdecode_der)
    except Exception as e:
        logger.error(f"ECDSA verification error: {e}")
        return False

# --- Logging Middleware ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    log_id = secrets.token_hex(4)
    logger.info(f"RID {log_id} --> {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}")
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(f"RID {log_id} <-- {request.method} {request.url.path} - Status: {response.status_code} ({process_time:.2f}ms)")
        return response
    except Exception as e:
        logger.error(f"RID {log_id} !!! {request.method} {request.url.path} - Unhandled Error: {e}", exc_info=True)
        raise e

# --- API Endpoints ---

@app.get("/api/signup-mnemonics", response_model=dict[str, list[str]], tags=["Auth"])
async def get_signup_mnemonics():
    """Generates three unique 12-word BIP39 mnemonics for client-side selection."""
    logger.debug("Generating mnemonics requested.")
    try:
        mnemo = Mnemonic("english")
        mnemonics = [mnemo.generate(strength=128) for _ in range(3)]
        logger.info(f"Generated {len(mnemonics)} mnemonics for signup selection.")
        return {"mnemonics": mnemonics}
    except Exception as e:
        logger.error(f"Error generating mnemonics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate recovery phrase options")

@app.post("/api/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED, tags=["Auth"])
async def signup(req: SignupRequest, session: Session = Depends(get_session)):
    """Registers a new user with data prepared by the client (username, email, hashed_password, pubkey)."""
    logger.info(f"Signup attempt for username='{req.username}', email='{req.email}', pubkey='{req.pubkey[:10]}...'")

    try:
        PublicKey(bytes.fromhex(req.pubkey))
    except Exception:
        logger.warning(f"Signup failed for '{req.username}': Invalid public key format received: '{req.pubkey}'")
        raise HTTPException(status_code=400, detail="Invalid public key format.")

    existing_user = session.exec(
        select(User).where(
            (User.username == req.username) | (User.email == req.email) | (User.pubkey == req.pubkey)
        )
    ).first()

    if existing_user:
        field = "Username"
        if existing_user.email == req.email: field = "Email"
        elif existing_user.pubkey == req.pubkey: field = "Public key identifier"
        logger.warning(f"Signup failed for '{req.username}': Conflict - {field} already exists.")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{field} already registered.")

    new_user = User(
        username=req.username, email=req.email,
        hashed_password=req.hashed_password,
        pubkey=req.pubkey
    )
    session.add(new_user)

    try:
        session.commit()
        session.refresh(new_user)
        logger.success(f"User '{new_user.username}' registered successfully (ID: {new_user.id}).")
        return SignupResponse(success=True, message="Signup successful! You can now log in.")
    except Exception as e:
        session.rollback()
        logger.error(f"Database error during signup commit for '{req.username}': {e}", exc_info=True)
        if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
            logger.warning(f"Signup conflict during commit for '{req.username}' (likely race condition or re-submission).")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account identifier already exists.")
        raise HTTPException(status_code=500, detail="Failed to save user data due to a server error.")

@app.post("/api/auth/challenge", response_model=ChallengeResponse, tags=["Auth"])
async def get_auth_challenge(req: ChallengeRequest, session: Session = Depends(get_session)):
    """Provides a unique challenge for a given public key if the user exists."""
    logger.info(f"Challenge requested for pubkey: '{req.pubkey[:10]}...'")

    user = session.exec(select(User).where(User.pubkey == req.pubkey)).first()
    if not user:
        logger.warning(f"Challenge requested for non-existent pubkey: '{req.pubkey}'")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No account found for this identifier.")

    challenge_bytes = secrets.token_bytes(32)
    challenge_hex = challenge_bytes.hex()
    challenge_store[req.pubkey] = (challenge_hex, time.time())
    logger.info(f"Generated challenge '{challenge_hex[:8]}...' for pubkey '{req.pubkey[:10]}...'")

    current_time = time.time()
    if secrets.randbelow(10) == 0:
        keys_to_delete = [pk for pk, (_, ts) in challenge_store.items() if current_time - ts > CHALLENGE_TTL]
        if keys_to_delete:
            logger.debug(f"Challenge store cleanup: Removing {len(keys_to_delete)} expired challenges.")
            for pk in keys_to_delete:
                try: del challenge_store[pk]
                except KeyError: pass

    return ChallengeResponse(challengeHex=challenge_hex)

@app.post("/api/auth/login", response_model=LoginResponse, tags=["Auth"])
async def login(req: LoginRequest, session: Session = Depends(get_session)):
    """Verifies the ECDSA signature against the stored challenge."""
    logger.info(f"Login attempt for pubkey: '{req.pubkey[:10]}...'")

    challenge_data = challenge_store.pop(req.pubkey, None)
    current_time = time.time()

    if not challenge_data:
        logger.warning(f"Login failed for '{req.pubkey}': No valid challenge found.")
        raise HTTPException(status_code=400, detail="Login session invalid or expired. Please try initiating login again.")

    stored_challenge_hex, timestamp = challenge_data
    if current_time - timestamp > CHALLENGE_TTL:
        logger.warning(f"Login failed for '{req.pubkey}': Challenge expired.")
        raise HTTPException(status_code=400, detail="Login session expired. Please try again.")
    if stored_challenge_hex != req.challengeHex:
        logger.warning(f"Login failed for '{req.pubkey}': Challenge mismatch.")
        raise HTTPException(status_code=400, detail="Login session data mismatch. Please try again.")

    user = session.exec(select(User).where(User.pubkey == req.pubkey)).first()
    if not user:
        logger.error(f"CRITICAL: Login failed for '{req.pubkey}': User not found in DB despite valid challenge!")
        raise HTTPException(status_code=404, detail="User account inconsistency. Please contact support.")

    try:
        is_valid = verify_ecdsa_signature(
            req.pubkey, 
            req.signature_der, 
            bytes.fromhex(req.challengeHex)
        )
        
        logger.debug(f"ECDSA verification for {user.username}: {is_valid}")

    except Exception as e:
        logger.error(f"ECDSA verification internal error for '{user.username}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Signature verification failed internally.")

    if is_valid:
        logger.success(f"Login successful for user '{user.username}' (pubkey: {req.pubkey}).")
        return LoginResponse(success=True, message="Login successful!", username=user.username)
    else:
        logger.warning(f"Login failed for '{user.username}' (pubkey: {req.pubkey}): Invalid ECDSA signature.")
        raise HTTPException(status_code=401, detail="Authentication failed: Invalid signature.")

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Backend is running."}

