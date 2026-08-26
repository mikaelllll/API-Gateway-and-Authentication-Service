import hashlib, secrets
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from app.config import get_settings

password_hasher = PasswordHash.recommended()
settings = get_settings()
def hash_password(password: str) -> str: return password_hasher.hash(password)
def verify_password(password: str, hashed: str) -> bool: return password_hasher.verify(password, hashed)
def digest(value: str) -> str: return hashlib.sha256(value.encode()).hexdigest()
def create_access_token(user_id: str, role: str) -> tuple[str, int]:
    seconds = settings.access_token_minutes * 60
    now = datetime.now(timezone.utc)
    payload = {"sub": user_id, "role": role, "type": "access", "iat": now, "exp": now + timedelta(seconds=seconds), "jti": secrets.token_urlsafe(16)}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256"), seconds
def decode_access_token(token: str) -> dict:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    if payload.get("type") != "access": raise jwt.InvalidTokenError("Wrong token type")
    return payload
def new_refresh_token() -> str: return secrets.token_urlsafe(48)
def new_api_key() -> str: return "sgw_" + secrets.token_urlsafe(32)

