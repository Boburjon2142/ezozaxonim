from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserProfileOut, UserProfileUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfileOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserProfileOut)
def update_me(payload: UserProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(current_user, key, value)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/export")
def export_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {
        "profile": {
            "email": current_user.email,
            "timezone": current_user.timezone,
            "goals": current_user.goals,
        },
        "sessions": len(current_user.time_sessions),
        "checkins": len(current_user.checkins),
        "plans": len(current_user.plans),
    }


@router.delete("/me")
def delete_account(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
    return {"status": "deleted"}
