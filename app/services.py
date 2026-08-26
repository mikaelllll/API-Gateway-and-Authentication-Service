import json
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.models import AuditLog, RefreshToken, User
from app.schemas import TokenPair
from app.security import create_access_token, digest, new_refresh_token

async def audit(db: AsyncSession, action: str, outcome: str, actor_id=None, ip=None, details=None):
    db.add(AuditLog(actor_id=actor_id, action=action, outcome=outcome, ip_address=ip, details=json.dumps(details) if details else None))
    await db.commit()

async def issue_tokens(db: AsyncSession, user: User) -> TokenPair:
    raw = new_refresh_token()
    expires = datetime.now(timezone.utc) + timedelta(days=get_settings().refresh_token_days)
    db.add(RefreshToken(user_id=user.id, token_hash=digest(raw), expires_at=expires))
    await db.commit()
    access, seconds = create_access_token(user.id, user.role.value)
    return TokenPair(access_token=access, refresh_token=raw, expires_in=seconds)

