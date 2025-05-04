import secrets
import time
from typing import Dict, Tuple, Optional
import hashlib
from loguru import logger
import coincurve
from fastapi import HTTPException, status

challenge_store: Dict[str, Tuple[str, float, str]] = {}  
def generate_challenge() -> str:
    return secrets.token_hex(32)

def schnorr_verify_commitment(pubkey_hex: str) -> Tuple[str, str]:
    logger.debug(f"Generating challenge for pubkey: {pubkey_hex[:10]}...")
    challenge = generate_challenge()
    challenge_store[pubkey_hex] = (challenge, time.time(), None)
    logger.info(f"Challenge generated for pubkey {pubkey_hex[:10]}...")
    logger.debug(f"Challenge value: {challenge[:16]}...")
    
    return challenge

def schnorr_verify_response(pubkey_hex: str, challenge_hex: str, R_hex: str, s_hex: str) -> Tuple[bool, Optional[str]]:
    logger.info(f"Verifying Schnorr ZKP for pubkey: {pubkey_hex[:10]}...")
    
    if pubkey_hex not in challenge_store:
        logger.warning(f"No active challenge session for pubkey: {pubkey_hex[:10]}...")
        return False, "No active challenge session"
    
    stored_challenge, timestamp, _ = challenge_store.pop(pubkey_hex)
    
    if challenge_hex != stored_challenge:
        logger.warning(f"Challenge mismatch for pubkey: {pubkey_hex[:10]}...")
        return False, "Challenge mismatch"
    
    if time.time() - timestamp > 300:
        logger.warning(f"Challenge expired for pubkey: {pubkey_hex[:10]}...")
        return False, "Challenge expired"
    
    try:
        pubkey_bytes = bytes.fromhex(pubkey_hex)
        R_bytes = bytes.fromhex(R_hex)
        s_bytes = bytes.fromhex(s_hex)
        challenge_bytes = bytes.fromhex(challenge_hex)
        
        logger.debug(f"Schnorr verification components:")
        logger.debug(f"  R: {R_hex[:16]}...")
        logger.debug(f"  s: {s_hex[:16]}...")
        logger.debug(f"  challenge: {challenge_hex[:16]}...")
        
        try:
            public_key_point = coincurve.PublicKey(pubkey_bytes)
            R_point = coincurve.PublicKey(R_bytes)
        except Exception as e:
            logger.error(f"Invalid point encoding: {e}")
            return False, "Invalid public key or commitment"
        
        e_bytes = hashlib.sha256(R_bytes + pubkey_bytes + challenge_bytes).digest()
        s_G = coincurve.PublicKey.from_secret(s_bytes) # Verify: s*G = R + e*P
        e_times_pubkey = public_key_point.multiply(e_bytes) # e * public_key (scalar multiplication)
        expected = R_point.combine([e_times_pubkey]) # R + e*public_key (point addition)
        
        is_valid = s_G.format() == expected.format()
        
        if is_valid:
            logger.info(f"Schnorr ZKP verification successful for pubkey: {pubkey_hex[:10]}...")
        else:
            logger.warning(f"Schnorr ZKP verification failed for pubkey: {pubkey_hex[:10]}...")
            
        return is_valid, None
        
    except Exception as e:
        logger.error(f"Error during Schnorr verification: {str(e)}")
        return False, f"Verification error: {str(e)}"