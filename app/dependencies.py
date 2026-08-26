from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import ApiKey, Role, User
from app.security import decode_access_token, digest

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/oauth/token", auto_error=False)
async def current_user(token: str | None = Depends(oauth2), db: AsyncSession = Depends(get_db)) -> User:
    if not token: raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Bearer token required")
    try: payload = decode_access_token(token)
    except InvalidTokenError: raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    user = await db.get(User, payload["sub"])
    if not user or not user.is_active: raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Inactive user")
    return user
def require_roles(*roles: Role):
    async def check(user: User = Depends(current_user)):
        if user.role not in roles: raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient role")
        return user
    return check
async def api_key_user(x_api_key: str = Header(...), db: AsyncSession = Depends(get_db)) -> User:
    result = await db.execute(select(ApiKey).where(ApiKey.key_hash == digest(x_api_key), ApiKey.is_active.is_(True)))
    key = result.scalar_one_or_none()
    if not key: raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid API key")
    user = await db.get(User, key.user_id)
    if not user or not user.is_active: raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Inactive owner")
    return user
