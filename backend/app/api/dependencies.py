from fastapi import Depends
from sqlmodel import Session
from mnemonic import Mnemonic
from app.db.session import get_session

def get_mnemonic_generator():
    return Mnemonic("english")

get_db = get_session