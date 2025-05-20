import * as secp from "@noble/secp256k1";
import { sha256 } from "@noble/hashes/sha2";
import { bytesToHex, hexToBytes, concatBytes } from "@noble/hashes/utils";
import { pbkdf2 } from "pbkdf2";

export class SchnorrAuth {
  static async deriveKeyPair(seedInput: string, password: string) {
    console.group("🔑 Deriving Key Pair from Seed + Password");

    try {
      const isHexSeed = /^[0-9a-fA-F]{64}$/.test(seedInput.trim());

      let seed: Uint8Array;
      if (isHexSeed) {
        console.log("📊 Using direct hex seed format");
        const hexSeed = seedInput.trim();
        seed = new Uint8Array(
          hexSeed.match(/.{1,2}/g)!.map((byte) => parseInt(byte, 16))
        );
      } else {
        console.log("📝 Using BIP39 mnemonic format");
        const passwordBytes = new TextEncoder().encode(`mnemonic${password}`);
        seed = await new Promise<Uint8Array>((resolve, reject) => {
          pbkdf2(
            new TextEncoder().encode(seedInput),
            passwordBytes,
            2048,
            64,
            "SHA-512",
            (err, derivedKey) => {
              if (err) reject(err);
              else resolve(new Uint8Array(derivedKey));
            }
          );
        });
      }
      if (!seed) {
        throw new Error("Failed to derive seed");
      }

      console.log(
        `📦 Base seed generated: ${Buffer.from(seed)
          .toString("hex")
          .substring(0, 16)}...`
      );

      const passwordHash = sha256(new TextEncoder().encode(password));
      console.log(
        `🔒 Password hash: ${bytesToHex(passwordHash).substring(0, 16)}...`
      );

      const tweakedSeed = new Uint8Array(seed).slice(0, 32);
      for (let i = 0; i < 32; i++) {
        tweakedSeed[i] = tweakedSeed[i] ^ passwordHash[i % passwordHash.length];
      }
      console.log(
        `🔄 Combined seed+password: ${bytesToHex(tweakedSeed).substring(
          0,
          16
        )}...`
      );

      const privateKey = tweakedSeed;

      const publicKey = secp.getPublicKey(privateKey, true);
      console.log(
        `🔐 Public Key: ${bytesToHex(publicKey).substring(0, 16)}...`
      );

      console.log("✅ Key pair derived successfully");
      console.groupEnd();

      return {
        privateKey,
        publicKey: bytesToHex(publicKey),
      };
    } catch (error) {
      console.error("❌ Failed to derive key pair:", error);
      console.groupEnd();
      throw error;
    }
  }

  static async authenticate(
    apiBaseUrl: string,
    privateKey: Uint8Array,
    publicKeyHex: string
  ) {
    console.group("🔒 Schnorr ZKP Authentication");

    try {
      console.log("📤 Requesting challenge from server...");
      const challengeResponse = await fetch(
        `${apiBaseUrl}/api/auth/challenge`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ pubkey: publicKeyHex }),
        }
      );

      if (!challengeResponse.ok) {
        const error = await challengeResponse.json();
        throw new Error(error.detail || "Failed to get challenge");
      }

      const { challengeHex } = await challengeResponse.json();
      console.log(`📩 Received challenge: ${challengeHex.substring(0, 16)}...`);

      console.log("🎲 Generating random nonce k...");
      const k = secp.utils.randomPrivateKey();
      console.log(`   Nonce generated: ${bytesToHex(k).substring(0, 16)}...`);

      console.log("📊 Calculating commitment R = k*G...");
      const R = secp.getPublicKey(k, true);
      const R_hex = bytesToHex(R);
      console.log(`   R = ${R_hex.substring(0, 16)}...`);

      console.log("🔄 Calculating challenge hash...");
      const challenge_bytes = hexToBytes(challengeHex);
      const pubkey_bytes = hexToBytes(publicKeyHex);

      const messageToHash = concatBytes(R, pubkey_bytes, challenge_bytes);
      const e = sha256(messageToHash);
      console.log(`   e = ${bytesToHex(e).substring(0, 16)}...`);

      console.log("📝 Calculating Schnorr response s = k + e*privateKey...");

      const eBigInt = SchnorrAuth.bytesToBigInt(e);
      const privateKeyBigInt = SchnorrAuth.bytesToBigInt(privateKey);
      const kBigInt = SchnorrAuth.bytesToBigInt(k);

      // Calculate s = k + e*privateKey mod n
      const curveN = secp.CURVE.n;
      const product = (eBigInt * privateKeyBigInt) % curveN;
      const sBigInt = (kBigInt + product) % curveN;

      const s = SchnorrAuth.bigIntToBytes(sBigInt);
      const s_hex = bytesToHex(s);
      console.log(`   s = ${s_hex.substring(0, 16)}...`);

      console.log("📤 Sending ZKP proof to server...");
      const loginResponse = await fetch(`${apiBaseUrl}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          pubkey: publicKeyHex,
          challengeHex,
          R_hex,
          s_hex,
        }),
      });

      if (!loginResponse.ok) {
        const error = await loginResponse.json();
        console.error("❌ Authentication failed:", error);
        console.groupEnd();
        throw new Error(error.detail || "Authentication failed");
      }

      const result = await loginResponse.json();
      console.log("✅ Authentication successful!", result);
      console.groupEnd();

      return result;
    } catch (error) {
      console.error("❌ Authentication error:", error);
      console.groupEnd();
      throw error;
    }
  }

  private static bytesToBigInt(bytes: Uint8Array): bigint {
    return BigInt("0x" + bytesToHex(bytes));
  }

  private static bigIntToBytes(num: bigint): Uint8Array {
    let hex = num.toString(16);
    if (hex.length % 2) hex = "0" + hex;
    while (hex.length < 64) hex = "0" + hex;
    return hexToBytes(hex);
  }
}
