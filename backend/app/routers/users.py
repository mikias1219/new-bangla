from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import SessionLocal
from ..models import User
from ..auth.jwt import get_current_user

router = APIRouter()

class UserUpdate(BaseModel):
    full_name: str = None
    phone_number: str = None
    bio: str = None
    avatar_url: str = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "phone_number": current_user.phone_number,
        "bio": current_user.bio,
        "avatar_url": current_user.avatar_url,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser,
        "created_at": current_user.created_at
    }

@router.put("/me")
async def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return {"message": "User updated successfully", "user": current_user}
