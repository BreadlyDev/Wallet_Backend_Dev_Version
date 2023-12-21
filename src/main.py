import uvicorn

from fastapi import FastAPI
from redis import RedisError
from starlette.middleware.cors import CORSMiddleware
from src.auth.routers import auth_router
from src.wallet import services
from src.wallet.services import *
# from src.wallet.services import get_coin_data, get_history_prices_coincap, get_history_prices_gecko, get_history_prices
from src.wallet.routers import wallet_router

app = FastAPI(
    title="Crypta"
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth endpoint
app.include_router(
    router=auth_router,
    prefix="/api/v1/auth",
    tags=["Auth"]
)

# Wallet endpoint
app.include_router(
    router=wallet_router,
    prefix="/api/v1/wallet",
    tags=["Wallet"],
)


@app.get('/Hello', tags=["Hello"])
async def root():
    return {'message': 'Hello it\'s main_app'}


# @app.get('/api/v1/currency/get/prices/coincap', tags=["API"])
# async def get_prices_by_coincap(interval: str = "d1"):
#     return get_history_prices_coincap(interval=interval)
#
#
# @app.get('/api/v1/currency/get/prices/gecko', tags=["API"])
# async def get_prices_by_gecko(symbol: str = "bitcoin", vs_currency: str = "usd",
#                                 days: str | int = "90", interval: str = "daily"):
#     return get_history_prices_gecko(symbol=symbol, vs_currency=vs_currency,
#                                 days=days, interval=interval)


@app.websocket("/history/")
async def websocket_endpoint(websocket: WebSocket, coin_name: str, interval: str):
    await websocket.accept()
    await get_history_prices(websocket=websocket, coin_name=coin_name, interval=interval)


async def startup_event():
    print("Server is starting")


# @app.on_event("startup")
# async def on_startup():
#     try:
#         await get_currency_data()
#     except asyncio.TimeoutError as e:
#         print(e)
#     except RedisError as e:
#         print(e)

if __name__ == "__main__":
    uvicorn.run(app, port=8080, reload=True)
