import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from ecdsa import VerifyingKey, SECP256k1, util

challenge_store: Dict[str, Tuple[str, float]] = {}

def hash_sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def generate_challenge() -> str:
    return secrets.token_bytes(32).hex()

def verify_ecdsa_signature(pubkey_hex: str, signature_der: str, message: bytes) -> bool:
    try:
        pubkey_bytes = bytes.fromhex(pubkey_hex)
        if len(pubkey_bytes) != 33 or pubkey_bytes[0] not in (2, 3):
            return False
            
        vk = VerifyingKey.from_string(
            pubkey_bytes, 
            curve=SECP256k1,
            hashfunc=hashlib.sha256,
            validate_point=True
        )
        
        signature_bytes = bytes.fromhex(signature_der)
        
        msg_hash = hash_sha256(message)
        
        return vk.verify_digest(signature_bytes, msg_hash, sigdecode=util.sigdecode_der)
    except Exception:
        return False