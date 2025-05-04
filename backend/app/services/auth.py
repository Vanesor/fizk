import time
from loguru import logger
from sqlmodel import Session, select
from app.db.models import User
from app.core.security import challenge_store, verify_ecdsa_signature, generate_challenge
from app.core.config import settings
from typing import Optional, Tuple

class AuthService:
    @staticmethod
    def create_user(session: Session, username: str, email: str, hashed_password: str, pubkey: str) -> User:
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            pubkey=pubkey
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

    @staticmethod
    def get_user_by_pubkey(session: Session, pubkey: str) -> Optional[User]:
        return session.exec(select(User).where(User.pubkey == pubkey)).first()
    
    @staticmethod
    def create_challenge(pubkey: str) -> str:
        challenge = generate_challenge()
        challenge_store[pubkey] = (challenge, time.time())
        return challenge
        
    @staticmethod
    def verify_challenge(pubkey: str, challenge_hex: str) -> bool:
        stored = challenge_store.get(pubkey)
        if not stored:
            return False
        
        stored_challenge, timestamp = stored
        if time.time() - timestamp > settings.CHALLENGE_TTL:
            return False
            
        return stored_challenge == challenge_hex
        
    @staticmethod
    def verify_login(pubkey: str, challenge_hex: str, signature_der: str) -> Tuple[bool, Optional[str]]:
        stored = challenge_store.pop(pubkey, None)
        if not stored:
            return False, "Login session invalid or expired"
            
        stored_challenge, timestamp = stored
        if time.time() - timestamp > settings.CHALLENGE_TTL:
            return False, "Login session expired"
            
        if stored_challenge != challenge_hex:
            return False, "Challenge mismatch"
        
        try:
            message_bytes = bytes.fromhex(challenge_hex)
            is_valid = verify_ecdsa_signature(pubkey, signature_der, message_bytes)
            
            if not is_valid:
                return False, "Invalid signature"
                
            return True, None
        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False, "Signature verification error"