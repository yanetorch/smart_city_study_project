from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, ServiceApiKey
from app.database import get_db
from app.security import decode_token, hash_api_key
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
api_key_scheme = APIKeyHeader(name="X-API-Key")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    try:
        payload = decode_token(token)
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if "sub" not in payload:
        raise HTTPException(401)
    
    sub = payload["sub"]
    result = await db.execute(select(User).where(User.username == sub))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user

async def verify_service_key(key: str = Depends(api_key_scheme), db: AsyncSession = Depends(get_db)) -> ServiceApiKey:
    key_hash = hash_api_key(key)
    result = await db.execute(select(ServiceApiKey).where(ServiceApiKey.key_hash == key_hash, ServiceApiKey.is_active.is_(True)))
    service_key = result.scalar_one_or_none()

    if service_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return service_key