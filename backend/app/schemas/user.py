from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: EmailStr

class UserCreate(UserBase):
    hashed_password: str
    pubkey: str
    
    @field_validator('pubkey')
    @classmethod
    def validate_pubkey(cls, v):
        if not re.match(r'^(02|03)[0-9a-fA-F]{64}$', v):
            raise ValueError("Invalid public key format. Must start with '02' or '03' followed by 64 hex characters")
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if v is not None and (len(v) < 3 or len(v) > 100):
            raise ValueError("Username must be between 3 and 100 characters")
        return v

class UserInDB(UserBase):
    id: int
    pubkey: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    pubkey: str
    created_at: datetime

    class Config:
        from_attributes = True