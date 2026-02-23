import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(120), default="")
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    preferred_work_hours: Mapped[str] = mapped_column(String(64), default="09:00-17:00")
    goals: Mapped[str] = mapped_column(String(500), default="")
    push_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    plans = relationship("Plan", back_populates="user", cascade="all,delete")
    time_sessions = relationship("TimeSession", back_populates="user", cascade="all,delete")
    checkins = relationship("CheckIn", back_populates="user", cascade="all,delete")
    break_rule = relationship("BreakRule", back_populates="user", uselist=False, cascade="all,delete")
    notifications = relationship("NotificationLog", back_populates="user", cascade="all,delete")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all,delete")
    feature_flags = relationship("FeatureFlag", back_populates="user", cascade="all,delete")
    memberships = relationship("OrganizationMember", back_populates="user", cascade="all,delete")
