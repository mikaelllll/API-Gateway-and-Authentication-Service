from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from fastapi import Body, Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.database import create_schema, get_db
from app.dependencies import api_key_user, current_user, require_roles
from app.limiter import enforce_rate_limit
from app.models import ApiKey, AuditLog, RefreshToken, Role, User
from app.schemas import ApiKeyCreate, ApiKeyView, AuditView, LoginRequest, RefreshRequest, RegisterRequest, RevokeRequest, TokenPair, UserView
from app.security import digest, hash_password, new_api_key, verify_password
from app.services import audit, issue_tokens

@asynccontextmanager
async def lifespan(app):
    await create_schema(); yield

app = FastAPI(title="Sentinel API Gateway", version="1.0.0", lifespan=lifespan, docs_url="/api/docs", redoc_url="/api/redoc")
app.add_middleware(CORSMiddleware, allow_origins=get_settings().cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/"): await enforce_rate_limit(request)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Gateway"] = "Sentinel"
    return response

@app.get("/api/health")
async def health(): return {"status":"healthy","service":"sentinel-gateway","time":datetime.now(timezone.utc)}

@app.post("/api/auth/register", response_model=UserView, status_code=201)
async def register(body: RegisterRequest, request: Request, db: AsyncSession = Depends(get_db)):
    if (await db.execute(select(User).where(User.email == body.email.lower()))).scalar_one_or_none(): raise HTTPException(409, "Email already registered")
    user = User(email=body.email.lower(), password_hash=hash_password(body.password)); db.add(user); await db.commit(); await db.refresh(user)
    await audit(db,"user.registered","success",user.id,request.client.host if request.client else None)
    return user

@app.post("/api/auth/login", response_model=TokenPair)
async def login(body: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.email == body.email.lower()))).scalar_one_or_none()
    if not user or not user.password_hash or not verify_password(body.password,user.password_hash):
        await audit(db,"auth.login","failure",ip=request.client.host if request.client else None,details={"email":body.email}); raise HTTPException(401,"Invalid credentials")
    tokens = await issue_tokens(db,user); await audit(db,"auth.login","success",user.id,request.client.host if request.client else None); return tokens

@app.post("/api/oauth/token", response_model=TokenPair, tags=["OAuth2"])
async def oauth2_token(request: Request, form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """OAuth2 Resource Owner Password flow for first-party demo clients."""
    user = (await db.execute(select(User).where(User.email == form.username.lower()))).scalar_one_or_none()
    if not user or not user.password_hash or not verify_password(form.password, user.password_hash):
        await audit(db, "oauth2.token", "failure", ip=request.client.host if request.client else None)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials", headers={"WWW-Authenticate":"Bearer"})
    tokens = await issue_tokens(db, user)
    await audit(db, "oauth2.token", "success", user.id, request.client.host if request.client else None)
    return tokens

@app.post("/api/auth/refresh", response_model=TokenPair)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    token = (await db.execute(select(RefreshToken).where(RefreshToken.token_hash == digest(body.refresh_token)))).scalar_one_or_none()
    now=datetime.now(timezone.utc)
    if not token or token.revoked_at or token.expires_at.replace(tzinfo=timezone.utc) <= now: raise HTTPException(401,"Invalid refresh token")
    token.revoked_at=now; user=await db.get(User,token.user_id); await db.commit(); return await issue_tokens(db,user)

@app.post("/api/auth/revoke", status_code=204)
async def revoke(body: RevokeRequest, db: AsyncSession = Depends(get_db)):
    token=(await db.execute(select(RefreshToken).where(RefreshToken.token_hash==digest(body.refresh_token)))).scalar_one_or_none()
    if token and not token.revoked_at: token.revoked_at=datetime.now(timezone.utc); await db.commit()

@app.post("/api/lab/password-hash", tags=["Security Lab"])
async def password_hash_lab(password: str = Body(embed=True, min_length=10, max_length=128)):
    """Demonstrate one-way Argon2 hashing without exposing stored user credentials."""
    password_hash = hash_password(password)
    return {
        "algorithm": "Argon2",
        "hash": password_hash,
        "plaintext_stored": False,
        "verification_passed": verify_password(password, password_hash),
    }

@app.get("/api/lab/rate-limit", tags=["Security Lab"])
async def rate_limit_lab():
    """A safe target used by the frontend to demonstrate the gateway's 429 response."""
    return {"allowed": True, "limit": 60, "window_seconds": 60}

@app.get("/api/me", response_model=UserView)
async def me(user: User = Depends(current_user)): return user

@app.get("/api/admin/overview")
async def admin_overview(user: User = Depends(require_roles(Role.admin))): return {"message":"Admin RBAC check passed","actor":user.email}

@app.post("/api/api-keys", response_model=ApiKeyView, status_code=201)
async def create_key(body: ApiKeyCreate, user: User=Depends(current_user), db: AsyncSession=Depends(get_db)):
    raw=new_api_key(); key=ApiKey(user_id=user.id,name=body.name,prefix=raw[:12],key_hash=digest(raw)); db.add(key); await db.commit(); await db.refresh(key)
    return ApiKeyView(id=key.id,name=key.name,prefix=key.prefix,key=raw)

@app.get("/api/service/data")
async def service_data(user: User=Depends(api_key_user)): return {"authenticated":True,"method":"API key","owner":user.email,"data":["gateway","identity","policy"]}

@app.get("/api/audit", response_model=list[AuditView])
async def audit_logs(user: User=Depends(current_user), db: AsyncSession=Depends(get_db)):
    query=select(AuditLog).order_by(desc(AuditLog.created_at)).limit(50)
    if user.role not in (Role.admin,Role.auditor): query=query.where(AuditLog.actor_id==user.id)
    return list((await db.execute(query)).scalars())

dist=Path(__file__).parent.parent/"frontend"/"dist"
if dist.exists():
    app.mount("/assets",StaticFiles(directory=dist/"assets"),name="assets")
    @app.get("/{path:path}")
    async def spa(path: str): return FileResponse(dist/"index.html")
