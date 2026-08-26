from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models import Role

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128, pattern=r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+$")
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
class RefreshRequest(BaseModel): refresh_token: str
class RevokeRequest(BaseModel): refresh_token: str
class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
class UserView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: EmailStr
    role: Role
    is_active: bool
    oauth_provider: str | None
    created_at: datetime
class ApiKeyCreate(BaseModel): name: str = Field(min_length=2, max_length=80)
class ApiKeyView(BaseModel): id: str; name: str; prefix: str; key: str
class AuditView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str; actor_id: str | None; action: str; outcome: str; ip_address: str | None; details: str | None; created_at: datetime

