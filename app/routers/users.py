from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, verify_service_key
from app.models import ServiceApiKey, User
from app.schemas import UserPrivate, UserPublic

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserPrivate)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db), _: ServiceApiKey = Depends(verify_service_key)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(404, "User not found")

    return user

@router.get("", response_model=list[UserPublic])
async def list_users(db: AsyncSession = Depends(get_db), _: ServiceApiKey = Depends(verify_service_key)):
    result = await db.execute(select(User).order_by(User.id))
    users = result.scalars().all()

    return users