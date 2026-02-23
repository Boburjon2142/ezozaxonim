from datetime import date

from sqlalchemy.orm import Session

from app.models.checkin import CheckIn
from app.models.notification import NotificationLog


def adaptive_rule_adjustment(db: Session, user_id: str, focus_min: int, break_min: int) -> dict:
    latest = db.query(CheckIn).filter(CheckIn.user_id == user_id).order_by(CheckIn.date.desc()).first()
    recent_notifications = (
        db.query(NotificationLog)
        .filter(NotificationLog.user_id == user_id)
        .order_by(NotificationLog.scheduled_at.desc())
        .limit(3)
        .all()
    )
    ignored_three = len(recent_notifications) == 3 and all(n.acknowledged_at is None for n in recent_notifications)

    adjusted_focus = focus_min
    adjusted_break = break_min

    if latest and (latest.stress >= 4 or latest.energy <= 2):
        adjusted_focus = max(15, focus_min - 5)
        adjusted_break = min(20, break_min + 3)

    if ignored_three:
        adjusted_break = min(25, adjusted_break + 5)

    return {
        "date": date.today().isoformat(),
        "focus_min": adjusted_focus,
        "break_min": adjusted_break,
        "reason": "heuristic",
    }
