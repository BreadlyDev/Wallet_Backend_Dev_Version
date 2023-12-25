from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from . import services, schemas

wallet_router = APIRouter()


@wallet_router.get("/get/wallet")
async def get_wallet(user_id: int, session: AsyncSession = Depends(get_async_session)):
    return await services.get__wallet(user_id=user_id, session=session)


@wallet_router.get("/get/all/wallet/data")
async def get_all_wallet_data(user_id: int, session: AsyncSession = Depends(get_async_session)):
    return await services.get__all__wallet__data(user_id=user_id, session=session)


@wallet_router.get("/get/all/transactions")
async def get_all_wallet_data(user_id: int, session: AsyncSession = Depends(get_async_session)):
    return await services.get__all__transaction(user_id=user_id, session=session)


@wallet_router.put("/set/balance")
async def set_balance(user_id: int, balance: schemas.BalanceChangeSchema, session: AsyncSession = Depends(get_async_session)):
    return await services.set__balance(user_id=user_id, balance=balance, session=session)


@wallet_router.post("/buy/currency")
async def buy_currency(user_id: int, transaction: schemas.PurchaseCoinSchema, session: AsyncSession = Depends(get_async_session)):
    return await services.buy__currency(user_id=user_id, transaction=transaction, session=session)


@wallet_router.post("/sell/currency")
async def sell_currency(user_id: int, transaction: schemas.SaleCoinSchema, session: AsyncSession = Depends(get_async_session)):
    return await services.sell__currency(user_id=user_id, transaction=transaction, session=session)


@wallet_router.post("/swap/currency")
async def swap_currency(user_id: int, transaction: schemas.SwapCoinSchema, session: AsyncSession = Depends(get_async_session)):
    return await services.swap__currency(user_id=user_id, transaction=transaction, session=session)


@wallet_router.post("/create/currency")
async def create_currency(currency: schemas.CurrencyCreateSchema, session: AsyncSession = Depends(get_async_session)):
    return await services.create__currency(currency=currency, session=session)
