from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.database import Base
from sqlalchemy import ForeignKey, String
from datetime import datetime


TRANSACTION_OPERATIONS = [
    "PURCHASE", "SALE", "SWAP"
]


class Wallet(Base):
    __tablename__ = "wallet"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", onupdate="NO ACTION", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    user = relationship("User", back_populates="wallet")
    currency = relationship("Currency", back_populates="wallet")
    transaction = relationship("Transaction", back_populates="wallet")


class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallet.id", onupdate="NO ACTION", ondelete="CASCADE"), nullable=False)
    currency: Mapped[str] = mapped_column(String(100), nullable=False)
    currency_2: Mapped[str] = mapped_column(String(100), nullable=True)
    quantity: Mapped[int] = mapped_column(default=0, nullable=False)
    price: Mapped[int] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)
    executed_at: Mapped[datetime] = mapped_column(default=datetime.now)

    wallet = relationship("Wallet", back_populates="transaction")


class Currency(Base):
    __tablename__ = "currency"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallet.id", onupdate="NO ACTION", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[float] = mapped_column(default=0, nullable=False)

    wallet = relationship("Wallet", back_populates="currency")
