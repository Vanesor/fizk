from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.models import User
from app.core.exceptions import AuthError, NotFoundError, ConflictError
from app.schemas.auth import (
    ChallengeRequest, ChallengeResponse, LoginRequest, SchnorrLoginRequest,
    LoginResponse, SignupRequest, SignupResponse, MnemonicResponse
)
from app.services.auth import AuthService
from app.api.dependencies import get_db, get_mnemonic_generator
from app.db.crud.users import user as user_crud
from loguru import logger

router = APIRouter()

@router.get("/signup-mnemonics", response_model=MnemonicResponse)
async def get_signup_mnemonics(mnemonic_generator = Depends(get_mnemonic_generator)):
    logger.debug("Generating mnemonics requested.")
    try:
        mnemonics = [mnemonic_generator.generate(strength=128) for _ in range(3)]
        logger.info(f"Generated {len(mnemonics)} mnemonics for signup selection.")
        return MnemonicResponse(mnemonics=mnemonics)
    except Exception as e:
        logger.error(f"Error generating mnemonics: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate recovery phrase options")

@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(req: SignupRequest, db: Session = Depends(get_db)):
    logger.info(f"Signup attempt for username='{req.username}', email='{req.email}', pubkey='{req.pubkey[:10]}...'")

    if user_crud.exists_by_fields(db, username=req.username, email=req.email, pubkey=req.pubkey):
        field = "Username"
        existing_user = None
        
        if existing_user := user_crud.get_by_username(db, username=req.username):
            field = "Username"
        elif existing_user := user_crud.get_by_email(db, email=req.email):
            field = "Email"
        elif existing_user := user_crud.get_by_pubkey(db, pubkey=req.pubkey):
            field = "Public key"
            
        logger.warning(f"Signup failed for '{req.username}': Conflict - {field} already exists.")
        raise ConflictError(f"{field} already registered")

    try:
        user = AuthService.create_user(
            session=db,
            username=req.username,
            email=req.email,
            hashed_password=req.hashed_password,
            pubkey=req.pubkey
        )
        logger.success(f"User '{user.username}' registered successfully (ID: {user.id}).")
        return SignupResponse(success=True, message="Signup successful! You can now log in.")
    except Exception as e:
        logger.error(f"Database error during signup: {e}")
        raise HTTPException(status_code=500, detail="Failed to save user data")

@router.post("/challenge", response_model=ChallengeResponse)
async def get_auth_challenge(req: ChallengeRequest, db: Session = Depends(get_db)):
    logger.info(f"Challenge requested for pubkey: '{req.pubkey[:10]}...'")
    
    user = user_crud.get_by_pubkey(db, pubkey=req.pubkey)
    if not user:
        logger.warning(f"Challenge requested for non-existent pubkey: '{req.pubkey[:10]}...'")
        raise NotFoundError("No account found with this identifier")
    
    challenge = AuthService.create_challenge(req.pubkey)
    logger.info(f"Generated challenge '{challenge[:8]}...' for pubkey '{req.pubkey[:10]}...'")
    
    return ChallengeResponse(challengeHex=challenge)

@router.post("/login", response_model=LoginResponse)
async def login(req: SchnorrLoginRequest, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for pubkey: '{req.pubkey[:10]}...'")
    
    user = user_crud.get_by_pubkey(db, pubkey=req.pubkey)
    if not user:
        logger.warning(f"Login attempt for non-existent pubkey: '{req.pubkey[:10]}...'")
        raise NotFoundError("User not found")
    
    logger.debug(f"Schnorr ZKP authentication for user '{user.username}':")
    logger.debug(f"  R: {req.R_hex[:16]}...")
    logger.debug(f"  s: {req.s_hex[:16]}...")
    logger.debug(f"  challenge: {req.challengeHex[:16]}...")
    
    success, error_msg = AuthService.verify_login(
        req.pubkey, req.challengeHex, req.R_hex, req.s_hex
    )
    
    if not success:
        logger.warning(f"Login failed for '{user.username}': {error_msg}")
        raise AuthError(f"Authentication failed: {error_msg}")
    
    logger.success(f"Login successful for user '{user.username}' (pubkey: {req.pubkey[:10]}...)")
    return LoginResponse(success=True, message="Login successful!", username=user.username)