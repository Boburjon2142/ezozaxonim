import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    reflection: Mapped[str] = mapped_column(String(1000), default="")

    user = relationship("User", back_populates="plans")
    items = relationship("PlanItem", back_populates="plan", cascade="all,delete")


class PlanItem(Base):
    __tablename__ = "plan_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id: Mapped[str] = mapped_column(String, ForeignKey("plans.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(30), default="todo")
    estimate_minutes: Mapped[int] = mapped_column(Integer, default=25)
    tags: Mapped[str] = mapped_column(String(255), default="")

    plan = relationship("Plan", back_populates="items")
    time_sessions = relationship("TimeSession", back_populates="plan_item")
