from pydantic import BaseModel
from datetime import datetime


class WalletCreateSchema(BaseModel):
    user_id: int


class WalletReadSchema(BaseModel):
    id: int
    user: str
    created_time: datetime


class CurrencyCreateSchema(BaseModel):
    wallet_id: int
    name: str
    quantity: int | float


class CurrencyReadSchema(BaseModel):
    name: str
    quantity: int | float


class CurrencyChangeSchema(BaseModel):
    name: str
    quantity: int | float


class BalanceSetSchema(CurrencyCreateSchema):
    wallet_id: int
    name: str = "USDT"
    quantity: int | float = 100000


class BalanceChangeSchema(CurrencyChangeSchema):
    name: str = "USDT"


class TransactionCreateSchema(BaseModel):
    currency: str
    currency_2: None
    quantity: int | float
    type: str


class PurchaseCoinSchema(TransactionCreateSchema):
    type: str = "PURCHASE"


class SaleCoinSchema(TransactionCreateSchema):
    type: str = "SALE"


class SwapCoinSchema(TransactionCreateSchema):
    currency_2: str
    type: str = "SWAP"
