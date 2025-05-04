import time
from loguru import logger
from sqlmodel import Session, select
from app.db.models import User
from app.core.security import challenge_store, schnorr_verify_response, generate_challenge
from app.core.config import settings
from typing import Optional, Tuple

class AuthService:
    @staticmethod
    def create_user(session: Session, username: str, email: str, hashed_password: str, pubkey: str) -> User:
        logger.info(f"Creating new user account for: {username}, public key: {pubkey[:10]}...")
        
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            pubkey=pubkey
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        logger.info(f"User account created for: {username}, ID: {new_user.id}")
        return new_user

    @staticmethod
    def get_user_by_pubkey(session: Session, pubkey: str) -> Optional[User]:
        user = session.exec(select(User).where(User.pubkey == pubkey)).first()
        if user:
            logger.debug(f"Found user with pubkey {pubkey[:10]}...: {user.username}")
        else:
            logger.debug(f"No user found with pubkey {pubkey[:10]}...")
        return user
    
    @staticmethod
    def create_challenge(pubkey: str) -> str:
        logger.info(f"Creating challenge for pubkey: {pubkey[:10]}...")
        challenge = generate_challenge()
        challenge_store[pubkey] = (challenge, time.time(), None)
        logger.info(f"Challenge created: {challenge[:16]}...")
        return challenge
        
    @staticmethod
    def verify_login(pubkey: str, challenge_hex: str, R_hex: str, s_hex: str) -> Tuple[bool, Optional[str]]:
        logger.info(f"Verifying Schnorr ZKP login for pubkey: {pubkey[:10]}...")
        
        success, error_msg = schnorr_verify_response(pubkey, challenge_hex, R_hex, s_hex)
        
        if success:
            logger.info(f"Login successful for pubkey: {pubkey[:10]}...")
        else:
            logger.warning(f"Login failed for pubkey: {pubkey[:10]}... Reason: {error_msg}")
        
        return success, error_msg