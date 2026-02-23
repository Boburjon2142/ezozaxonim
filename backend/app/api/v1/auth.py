from jose import JWTError, jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import enforce_auth_rate_limit
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.db.session import get_db
from app.models.break_rule import BreakRule
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.auth import LoginRequest, PasswordResetRequest, RefreshRequest, SignupRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse)
def signup(payload: SignupRequest, request: Request, db: Session = Depends(get_db), _: None = Depends(enforce_auth_rate_limit)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail={"code": "email_exists", "message": "Email already registered"})

    user = User(email=payload.email.lower(), hashed_password=get_password_hash(payload.password), full_name=payload.full_name)
    db.add(user)
    db.flush()

    db.add(BreakRule(user_id=user.id))
    db.add(Subscription(user_id=user.id, tier="free", status="active"))
    db.commit()

    return TokenResponse(access_token=create_access_token(user.id), refresh_token=create_refresh_token(user.id))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db), _: None = Depends(enforce_auth_rate_limit)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail={"code": "invalid_credentials", "message": "Invalid credentials"})

    return TokenResponse(access_token=create_access_token(user.id), refresh_token=create_refresh_token(user.id))


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest):
    try:
        token_data = jwt.decode(payload.refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        if token_data.get("type") != "refresh":
            raise ValueError("invalid type")
        user_id = token_data.get("sub")
    except (JWTError, ValueError) as exc:
        raise HTTPException(status_code=401, detail={"code": "invalid_refresh", "message": "Invalid refresh token"}) from exc

    return TokenResponse(access_token=create_access_token(user_id), refresh_token=create_refresh_token(user_id))


@router.post("/password-reset")
def password_reset_stub(payload: PasswordResetRequest):
    return {"status": "queued", "message": "Password reset email stubbed", "email": payload.email}


@router.get("/oauth/google/start")
def oauth_google_stub():
    return {"status": "stub", "message": "OAuth Google flow not configured in MVP"}
