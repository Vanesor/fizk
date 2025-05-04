import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional

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
    def validate_challenge(cls, v):
        if not re.match(r'^[0-9a-fA-F]{64}$', v):
            raise ValueError("Invalid challenge format")
        return v

class LoginResponse(BaseModel):
    success: bool
    message: str
    username: Optional[str] = None

class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: EmailStr
    hashed_password: str
    pubkey: str
    
    @field_validator('pubkey')
    @classmethod
    def validate_pubkey(cls, v):
        if not re.match(r'^(02|03)[0-9a-fA-F]{64}$', v):
            raise ValueError("Invalid public key format")
        return v

class SignupResponse(BaseModel):
    success: bool
    message: str

class MnemonicResponse(BaseModel):
    mnemonics: List[str]