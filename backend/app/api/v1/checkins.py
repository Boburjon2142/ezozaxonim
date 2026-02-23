from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.checkin import CheckIn
from app.models.user import User
from app.schemas.checkin import CheckInIn, CheckInOut

router = APIRouter(prefix="/checkins", tags=["checkins"])


@router.get("", response_model=list[CheckInOut])
def list_checkins(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(CheckIn).filter(CheckIn.user_id == current_user.id).order_by(CheckIn.date.desc()).limit(120).all()


@router.post("", response_model=CheckInOut)
def upsert_checkin(payload: CheckInIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    checkin = db.query(CheckIn).filter(CheckIn.user_id == current_user.id, CheckIn.date == payload.date).first()
    if not checkin:
        checkin = CheckIn(user_id=current_user.id, **payload.model_dump())
    else:
        for key, value in payload.model_dump().items():
            setattr(checkin, key, value)
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin


@router.get("/streak")
def streak(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    days = {c.date for c in db.query(CheckIn).filter(CheckIn.user_id == current_user.id).all()}
    today = date.today()
    count = 0
    while today in days:
        count += 1
        today = today.fromordinal(today.toordinal() - 1)
    return {"streak": count}
