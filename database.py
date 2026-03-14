"""
visa-bot/database.py
SQLAlchemy async ORM models + helpers.
"""

from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text,
    func, select, update, delete,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from config import settings

# ── Engine & session factory ──────────────────────────────────────────────────
engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


# ── Base ──────────────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── Models ────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)        # Telegram user_id
    username: Mapped[Optional[str]] = mapped_column(String(64))
    full_name: Mapped[Optional[str]] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    applicants: Mapped[list[Applicant]] = relationship(back_populates="user", cascade="all, delete-orphan")
    appointments: Mapped[list[Appointment]] = relationship(back_populates="user")


class Applicant(Base):
    __tablename__ = "applicants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    full_name: Mapped[str] = mapped_column(String(128))
    passport_number: Mapped[str] = mapped_column(String(32))
    date_of_birth: Mapped[str] = mapped_column(String(10))   # ISO: YYYY-MM-DD
    nationality: Mapped[str] = mapped_column(String(64))
    email: Mapped[str] = mapped_column(String(128))
    phone: Mapped[str] = mapped_column(String(32))
    visa_type: Mapped[str] = mapped_column(String(64))
    visa_center: Mapped[str] = mapped_column(String(128))
    provider: Mapped[str] = mapped_column(String(16), default="vfs")  # "vfs" | "tls"
    auto_book: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="applicants")
    appointments: Mapped[list[Appointment]] = relationship(back_populates="applicant")


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    applicant_id: Mapped[int] = mapped_column(Integer, ForeignKey("applicants.id", ondelete="CASCADE"))
    provider: Mapped[str] = mapped_column(String(16))
    slot_date: Mapped[Optional[str]] = mapped_column(String(20))
    slot_time: Mapped[Optional[str]] = mapped_column(String(10))
    visa_center: Mapped[Optional[str]] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), default="pending")
    # status values: pending | booked | failed | cancelled
    confirmation_ref: Mapped[Optional[str]] = mapped_column(String(64))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(back_populates="appointments")
    applicant: Mapped[Applicant] = relationship(back_populates="appointments")


class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    level: Mapped[str] = mapped_column(String(16))
    message: Mapped[str] = mapped_column(Text)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# ── Init ──────────────────────────────────────────────────────────────────────

async def init_db() -> None:
    """Create all tables (idempotent)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ── CRUD helpers ──────────────────────────────────────────────────────────────

async def get_or_create_user(
    session: AsyncSession,
    user_id: int,
    username: str | None = None,
    full_name: str | None = None,
) -> User:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(id=user_id, username=username, full_name=full_name)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def get_active_applicants(session: AsyncSession) -> list[Applicant]:
    result = await session.execute(
        select(Applicant).where(Applicant.is_active == True, Applicant.auto_book == True)
    )
    return list(result.scalars().all())


async def log_event(session: AsyncSession, level: str, message: str, user_id: int | None = None) -> None:
    entry = Log(level=level, message=message, user_id=user_id)
    session.add(entry)
    await session.commit()
