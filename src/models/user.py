from sqlalchemy import Column, ForeignKey, Integer, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from models import diary

user_book_table = Table(
    "user__user_book_table",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user__user.id"), primary_key=True),
    Column("book_id", Integer, ForeignKey("user__book.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "user__user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name: Mapped[str | None] = mapped_column()
    last_name: Mapped[str | None] = mapped_column()
    age: Mapped[int | None] = mapped_column()
    password: Mapped[str | None] = mapped_column()
    addresses: Mapped[list["Address"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    books: Mapped[list["Book"]] = relationship(secondary=user_book_table, back_populates="users")
    diaries: Mapped[list["diary.Diary"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )


class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str] = mapped_column(unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user__user.id"))

    user: Mapped["User"] = relationship(back_populates="addresses", lazy="selectin")


class Profile(Base):
    __tablename__ = "user__profile"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user__user.id", ondelete="CASCADE"))
    image: Mapped[str] = mapped_column()

    __table_args__ = (UniqueConstraint("user_id"),)


class Book(Base):
    __tablename__ = "user__book"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    title: Mapped[str]
    users: Mapped[list["User"]] = relationship(secondary=user_book_table, back_populates="books")
