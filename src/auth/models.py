from datetime import datetime
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyBaseOAuthAccountTable
from sqlalchemy import ForeignKey, Column, JSON, String
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import Base


class OAuthAccount(SQLAlchemyBaseOAuthAccountTable[int], Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    oauth_name: Mapped[str] = mapped_column(index=True, nullable=False)
    access_token: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[int] = mapped_column(nullable=True)
    refresh_token: Mapped[int] = mapped_column(nullable=True)
    account_id: Mapped[str] = mapped_column(index=True, nullable=False)
    account_email: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user = relationship("User", back_populates="oauth_accounts")


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    permissions = Column("permissions", JSON)
    user = relationship("User", back_populates="role", uselist=False)


class User(SQLAlchemyBaseUserTable[int], Base):

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    firstname: Mapped[str] = mapped_column(nullable=True)
    lastname: Mapped[str] = mapped_column(nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    registered_at: Mapped[datetime] = mapped_column(default=datetime.now)
    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
    )
    role = relationship("Role", back_populates="user", )
    wallet = relationship("Wallet", back_populates="user", uselist=False)
