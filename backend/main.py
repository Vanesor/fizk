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
    k_bytes = sha256(private_key.to_bytes(32, 'big') + message).digest()
    k = int.from_bytes(k_bytes, 'big') % n
    if k == 0:
        raise ValueError("Bad nonce")

    R = k * G
    parity = R.y() & 1
    r = R.x()

    P = private_key * G
    px = P.x()

    e_bytes = sha256(r.to_bytes(32, 'big') + px.to_bytes(32, 'big') + message).digest()
    e = int.from_bytes(e_bytes, 'big') % n

    s = (k + e * private_key) % n
    sig = r.to_bytes(32, 'big') + s.to_bytes(32, 'big')
    return sig.hex()

def verify_ecdsa_signature(pubkey_hex: str, signature_der: str, message: bytes) -> bool:
    try:
        pubkey_bytes = bytes.fromhex(pubkey_hex)
        if len(pubkey_bytes) != 33 or pubkey_bytes[0] not in (2, 3):
            logger.warning(f"Invalid public key format: {pubkey_hex[:10]}...")
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
    except Exception as e:
        logger.error(f"ECDSA verification error: {e}")
        return False

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

@app.get("/api/signup-mnemonics", response_model=dict[str, list[str]], tags=["Auth"])
async def get_signup_mnemonics():
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

