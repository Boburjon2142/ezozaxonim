import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class CheckIn(Base):
    __tablename__ = "checkins"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    energy: Mapped[int] = mapped_column(Integer)
    stress: Mapped[int] = mapped_column(Integer)
    mood: Mapped[int] = mapped_column(Integer)
    sleep: Mapped[int] = mapped_column(Integer)
    note: Mapped[str] = mapped_column(String(500), default="")

    user = relationship("User", back_populates="checkins")
