from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from models.user import User


class Diary(Base):
    __tablename__ = "diary__diary"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user__user.id"), index=True)
    user: Mapped["User"] = relationship(back_populates="diaries", lazy="selectin")
    notes: Mapped[list["Note"]] = relationship(
        back_populates="diary", cascade="all, delete-orphan", lazy="selectin"
    )


class Note(Base):
    __tablename__ = "diary__note"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    title: Mapped[str]
    content: Mapped[str]
    diary_id: Mapped[int] = mapped_column(ForeignKey("diary__diary.id"), index=True)
    diary: Mapped["Diary"] = relationship(back_populates="notes", lazy="selectin")

    __table_args__ = (UniqueConstraint("title", "diary_id"),)
