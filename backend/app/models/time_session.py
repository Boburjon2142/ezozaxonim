import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TimeSession(Base):
    __tablename__ = "time_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)
    plan_item_id: Mapped[str | None] = mapped_column(String, ForeignKey("plan_items.id"), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)
    tags: Mapped[str] = mapped_column(String(255), default="")

    user = relationship("User", back_populates="time_sessions")
    plan_item = relationship("PlanItem", back_populates="time_sessions")
