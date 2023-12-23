from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket

from src.database import get_async_session
from . import services, schemas

wallet_router = APIRouter()


@wallet_router.get("/get/wallet")
async def get_wallet(user_id: int, session: AsyncSession = Depends(get_async_session)):
    return await services.get__wallet(user_id=user_id, session=session)


@wallet_router.get("/get/all/wallet/data")
async def get_all_wallet_data(user_id: int, session: AsyncSession = Depends(get_async_session)):
    return await services.get__all__wallet__data(user_id=user_id, session=session)


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


@wallet_router.websocket("/ws/coin/price/")
async def get_currency_data(currency: str, websocket: WebSocket):
    await websocket.accept()
    await services.get_currency_data_from_redis(currency=currency, websocket=websocket)


@wallet_router.get("/coin/price/get/", tags=["API"])
def read_root(coin: str):
    return HTMLResponse(
        f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>WebSocket Example</title>
            </head>
            <body>
                <h1>WebSocket Example</h1>
                <ul id='tickerList'></ul>
                <script>
                try {{
                    var ws = new WebSocket(`ws://127.0.0.1:8080/api/v1/wallet/ws/coin/price/?coin={coin}`);
                    ws.onmessage = function(event) {{
                        var data = JSON.parse(event.data);
                        console.log(data);
                        var tickerList = document.getElementById('tickerList');
                        var listItem = document.createElement('li');
                        listItem.textContent = data;
                        tickerList.appendChild(listItem);
                    }};

                    window.addEventListener('beforeunload', function() {{
                        ws.close();
                    }});
                    }}
                    catch (e) {{
                        console.log(e);
                    }}
                </script>
            </body>
        </html>
        """
    )
# @wallet_router.get("/get/currency")
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
