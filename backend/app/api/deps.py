from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.rate_limit import rate_limiter
from app.db.session import get_db
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    creds_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "invalid_token", "message": "Could not validate credentials"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("type") != "access":
            raise creds_exc
        user_id = payload.get("sub")
    except JWTError as exc:
        raise creds_exc from exc

    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if not user:
        raise creds_exc
    return user


def enforce_auth_rate_limit(request: Request) -> None:
    key = f"auth:{request.client.host if request.client else 'unknown'}"
    rate_limiter.check(key)


def require_org_role(allowed_roles: set[str]):
    def _checker(current_user: User = Depends(get_current_user)) -> User:
        roles = {m.role for m in current_user.memberships}
        if not roles.intersection(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "forbidden", "message": "Insufficient organization permissions"},
            )
        return current_user

    return _checker
