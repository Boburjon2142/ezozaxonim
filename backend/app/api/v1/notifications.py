from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.notification import NotificationLog
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/break")
def schedule_break_notification(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = NotificationLog(user_id=current_user.id, type="break_alert", scheduled_at=datetime.utcnow(), sent_at=datetime.utcnow())
    db.add(row)
    db.commit()
    return {"status": "sent", "channel": "web_push_stub"}


@router.post("/{notification_id}/ack")
def acknowledge(notification_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = db.query(NotificationLog).filter(NotificationLog.id == notification_id, NotificationLog.user_id == current_user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Notification not found"})
    row.acknowledged_at = datetime.utcnow()
    db.add(row)
    db.commit()
    return {"status": "acknowledged"}


@router.post("/{notification_id}/snooze")
def snooze(notification_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = db.query(NotificationLog).filter(NotificationLog.id == notification_id, NotificationLog.user_id == current_user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Notification not found"})
    row.snoozed_count += 1
    db.add(row)
    db.commit()
    return {"status": "snoozed", "snoozed_count": row.snoozed_count}


@router.post("/email")
def email_stub():
    return {"status": "queued", "provider": "stub"}
