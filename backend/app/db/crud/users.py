from typing import Optional
from sqlmodel import Session, select
from app.db.models import User
from app.db.crud.base import CRUDBase
from app.schemas.user import UserCreate, UserUpdate

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.exec(select(User).where(User.email == email)).first()
    
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.exec(select(User).where(User.username == username)).first()
    
    def get_by_pubkey(self, db: Session, *, pubkey: str) -> Optional[User]:
        return db.exec(select(User).where(User.pubkey == pubkey)).first()
        
    def exists_by_fields(self, db: Session, *, username: str = None, email: str = None, pubkey: str = None) -> bool:
        query = select(User)
        conditions = []
        
        if username:
            conditions.append(User.username == username)
        if email:
            conditions.append(User.email == email)
        if pubkey:
            conditions.append(User.pubkey == pubkey)
            
        if conditions:
            for condition in conditions:
                query = query.where(condition)
                if db.exec(query).first():
                    return True
        return False

user = CRUDUser(User)