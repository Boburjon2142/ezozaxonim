from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.time_session import TimeSession
from app.models.user import User
from app.schemas.time_session import TimeSessionIn, TimeSessionOut, TimeSessionUpdate

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=list[TimeSessionOut])
def list_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(TimeSession)
        .filter(TimeSession.user_id == current_user.id)
        .order_by(TimeSession.started_at.desc())
        .limit(200)
        .all()
    )


@router.post("/start", response_model=TimeSessionOut)
def start_session(payload: TimeSessionIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    active = (
        db.query(TimeSession)
        .filter(TimeSession.user_id == current_user.id, TimeSession.ended_at.is_(None))
        .first()
    )
    if active:
        raise HTTPException(status_code=400, detail={"code": "active_session_exists", "message": "Stop current session first"})

    session = TimeSession(
        user_id=current_user.id,
        started_at=payload.started_at,
        tags=payload.tags,
        plan_item_id=payload.plan_item_id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("", response_model=TimeSessionOut)
def add_session(payload: TimeSessionIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    duration = 0
    if payload.ended_at:
        duration = max(0, int((payload.ended_at - payload.started_at).total_seconds() / 60))

    session = TimeSession(
        user_id=current_user.id,
        started_at=payload.started_at,
        ended_at=payload.ended_at,
        duration_minutes=duration,
        tags=payload.tags,
        plan_item_id=payload.plan_item_id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/{session_id}/stop", response_model=TimeSessionOut)
def stop_session(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(TimeSession).filter(TimeSession.id == session_id, TimeSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Session not found"})
    if session.ended_at:
        return session

    session.ended_at = datetime.utcnow()
    session.duration_minutes = max(0, int((session.ended_at - session.started_at).total_seconds() / 60))
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.patch("/{session_id}", response_model=TimeSessionOut)
def update_session(session_id: str, payload: TimeSessionUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(TimeSession).filter(TimeSession.id == session_id, TimeSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Session not found"})

    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(session, key, value)

    if session.ended_at:
        session.duration_minutes = max(0, int((session.ended_at - session.started_at).total_seconds() / 60))
    db.add(session)
    db.commit()
    db.refresh(session)
    return session
