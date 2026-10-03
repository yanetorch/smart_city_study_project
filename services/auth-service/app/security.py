import bcrypt
from app.config import settings
from datetime import datetime, timedelta, timezone
import jwt
from hashlib import sha256

def hash_password(password : str) -> str:
    return bcrypt.hashpw(bytes(password, encoding="utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(bytes(plain, encoding="utf-8"), bytes(hashed, encoding="utf-8"))

def create_token(subject: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": exp}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

def hash_api_key(api_key: str) -> str:
    return sha256(api_key.encode("utf-8")).hexdigest()