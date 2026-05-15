from datetime import datetime, timezone

from sqlalchemy import String, Enum, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

import enum


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    avatar: Mapped[str | None] = mapped_column(String(256), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    addresses: Mapped[list["Address"]] = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    cart_items: Mapped[list["CartItem"]] = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user", cascade="all, delete-orphan")
