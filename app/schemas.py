from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models import Role


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, password: str) -> str:
        requirements = (
            any(character.isupper() for character in password),
            any(character.islower() for character in password),
            any(character.isdigit() for character in password),
        )
        if not all(requirements):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, and one number"
            )
        return password


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class RevokeRequest(BaseModel):
    refresh_token: str


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


class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)


class ApiKeyView(BaseModel):
    id: str
    name: str
    prefix: str
    key: str


class AuditView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    actor_id: str | None
    action: str
    outcome: str
    ip_address: str | None
    details: str | None
    created_at: datetime
