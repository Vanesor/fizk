from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.models import User
from app.schemas.user import UserResponse, UserUpdate
from app.db.crud.users import user as user_crud
from app.api.dependencies import get_db
from app.core.exceptions import NotFoundError
from loguru import logger
from typing import List

router = APIRouter()

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.get(db, id=user_id)
    if not user:
        raise NotFoundError("User")
    return user

@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    return user_crud.get_multi(db, skip=skip, limit=limit)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, 
    user_update: UserUpdate, 
    db: Session = Depends(get_db)
):
    db_user = user_crud.get(db, id=user_id)
    if not db_user:
        raise NotFoundError("User")
    
    if user_update.username and user_update.username != db_user.username:
        if user_crud.get_by_username(db, username=user_update.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already registered"
            )
    
    if user_update.email and user_update.email != db_user.email:
        if user_crud.get_by_email(db, email=user_update.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
    
    return user_crud.update(db, db_obj=db_user, obj_in=user_update)