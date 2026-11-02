from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from .config import settings

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        # Расшифровываем токен, используя общий SECRET_KEY
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")# Предполагаем, что auth_service кладет id в "sub"
        if username is None:
            raise HTTPException(status_code=401, detail="Неверный токен")
        return {"username": username}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось проверить подлинность",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Зависимость для внутренних запросов между сервисами (например, webhook)
def verify_internal_api_key(x_api_key: str | None = None):
    if not x_api_key or x_api_key != settings.SERVICE_API_KEY:
        raise HTTPException(status_code=403, detail="Доступ запрещен: неверный ключ сервиса")
    return True