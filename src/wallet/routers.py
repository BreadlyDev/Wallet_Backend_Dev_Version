from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session
from . import services, schemas

wallet_router = APIRouter()


@wallet_router.get("/get")
async def get_wallet_router(user_id: int, session: AsyncSession = Depends(get_async_session)):
    return await services.get__wallet(user_id=user_id, session=session)


@wallet_router.post("/set/balance")
async def set_balance(user_id: int, balance_data: schemas.BalanceChangeSchema, session: AsyncSession = Depends(get_async_session)):
    return await services.set__balance(user_id=user_id, balance_data=balance_data, session=session)


@wallet_router.post("/buy/currency")
async def buy_currency(user_id: int, transaction: schemas.PurchaseCreateSchema, session: AsyncSession = Depends(get_async_session)):
    return await services.buy__currency(user_id=user_id, transaction=transaction, session=session)


@wallet_router.post("/sell/currency")
async def buy_currency(user_id: int, transaction: schemas.SaleCreateSchema, session: AsyncSession = Depends(get_async_session)):
    return await services.sell__currency(user_id=user_id, transaction=transaction, session=session)


# @wallet_router.get("/get/currency_data")
# async def get_currency_data_router():
#     return await get_currency_data()

# @wallet_router.post("create/currency")
# async def create_currency(user_id: int, transaction_data: TransactionCreateSchema, session: AsyncSession = Depends(get_async_session)):
#     result = create_currency(user_id=user_id, transaction_data=transaction_data, session=session)
#     return result


# @wallet_router.post()


# @wallet_router.get("/get")
# async def get_wallet(session: AsyncSession = Depends(get_async_session)):
#     query = select(Wallet).where(Wallet.user_id == User.id)
#     result = await session.execute(query)
#     return result.one()


# @wallet_router.post("/create")
# async def create_wallet(wallet_data: WalletCreateSchema, session: AsyncSession = Depends(get_async_session)):
#     stmt = insert(Wallet).values(**wallet_data.dict())
#     await session.execute(stmt)
#     return {"HTTP STATUS 201 CREATED": "Wallet was successfully created"}
