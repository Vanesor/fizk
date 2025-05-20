import * as bip39 from "bip39";

export const validateSeed = (seed: string) => {
  const trimmedSeed = seed.trim();

  const isValidMnemonic = bip39.validateMnemonic(trimmedSeed);
  const isValidHex = /^[0-9a-fA-F]{64}$/.test(trimmedSeed);

  return {
    isValidMnemonic,
    isValidHex,
    isValid: isValidMnemonic || isValidHex,
  };
};

export const formatSeed = (seed: string): string => {
  return seed.trim().replace(/\s+/g, " ").toLowerCase();
};
