import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class BreakRule(Base):
    __tablename__ = "break_rules"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), unique=True)
    focus_min: Mapped[int] = mapped_column(Integer, default=25)
    break_min: Mapped[int] = mapped_column(Integer, default=5)
    long_break_min: Mapped[int] = mapped_column(Integer, default=15)
    long_break_every: Mapped[int] = mapped_column(Integer, default=4)
    adaptive_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    user = relationship("User", back_populates="break_rule")
