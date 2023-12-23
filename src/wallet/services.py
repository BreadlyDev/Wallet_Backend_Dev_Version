import asyncio
import json

import requests
import websockets
from redis import RedisError

from sqlalchemy import insert, update, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import WebSocket, HTTPException
from starlette.websockets import WebSocketState

from src.database import async_session_maker
from src.config import BINANCE_WEBSOCKET_URL, CURRENCY_CACHE_TIME, BINANCE_WEBSOCKET_ALL_COINS_URL, BINANCE_CURRENCY_LIST
from src.database import redis_client
from src.auth.models import User
from . import schemas
from .models import Wallet, Currency, Transaction, TRANSACTION_OPERATIONS


# Checks
async def check_transaction_type(transaction_type: str):
    if transaction_type not in TRANSACTION_OPERATIONS:
        raise HTTPException(status_code=400, detail={"message": "Incorrect operation"})


async def check_user_exists(user_id: int, session: AsyncSession = async_session_maker()):
    try:
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        user = result.scalar()
        if not user:
            raise HTTPException(status_code=404, detail={"message": f"User not found"})
    except Exception as e:
        print(e)
    finally:
        await session.close()


async def check_wallet_exists(wallet_id: int, session: AsyncSession = async_session_maker()):
    query = select(Wallet).where(Wallet.id == wallet_id)
    result = await session.execute(query)
    wallet = result.scalar()
    if not wallet:
        raise HTTPException(status_code=404, detail={"message": f"Wallet not found"})


async def check_quantity(quantity: int):
    if quantity < 0:
        raise HTTPException(status_code=400, detail={"message": f"Quantity should be positive number"})


async def check_balance(balance: float, price: float, quantity: int):
    if balance < quantity * price:
        raise HTTPException(status_code=400, detail={"message": f"Your balance is less than transaction price"})


async def check_currency_exist(currency):
    if not currency or currency.quantity <= 0:
        raise HTTPException(status_code=400, detail={"message": f"You have no {currency.name} coin"})


async def check_c_quantity_not_negative(currency, sell_c_quantity):
    if currency.quantity - sell_c_quantity < 0:
        raise HTTPException(status_code=400, detail={"message": "You can't sell more coins than you have"})


async def check_price_exists(price):
    if not price:
        raise HTTPException(status_code=400, detail={"message": "Price not found"})


async def check_currency_in_list(currency):
    if currency not in BINANCE_CURRENCY_LIST and currency != "USDT":
        raise HTTPException(status_code=400, detail=
                {"message": "Currency not found. Unfortunately we don't support other currencies"})


# Wallet services
async def get__wallet(user_id: int, session: AsyncSession = async_session_maker()):
    try:
        query = select(Wallet).where(Wallet.user_id == user_id)
        result = await session.execute(query)
        wallet = result.scalar()
        return wallet
    except Exception as e:
        print(e)
    finally:
        await session.close()


async def create__wallet(wallet_data: schemas.WalletCreateSchema, session: AsyncSession = async_session_maker()):
    try:
        stmt = insert(Wallet).values(**wallet_data.model_dump())
        wallet = await session.execute(stmt)
        await session.commit()

        wallet_id = wallet.inserted_primary_key[0]
        balance_data = wallet_data.model_dump()
        balance_data["wallet_id"] = wallet_id

        await create__currency(currency=schemas.BalanceSetSchema(**balance_data))
    except Exception as e:
        print(e)
    finally:
        await session.close()


# Currency/Coin services
async def create__currency(currency: schemas.CurrencyCreateSchema, session: AsyncSession = async_session_maker()):
    try:
        await check_wallet_exists(wallet_id=currency.wallet_id, session=session)
        await check_currency_in_list(currency=currency.name)
        stmt = insert(Currency).values(**currency.model_dump())
        await session.execute(stmt)
        await session.commit()
    except Exception as e:
        print(e)
    finally:
        await session.close()


async def get__currency(wallet_id: int, currency: str, session: AsyncSession = async_session_maker()):
    try:
        await check_currency_in_list(currency=currency)
        query = select(Currency).where((Currency.name == currency) & (Currency.wallet_id == wallet_id))
        result = await session.execute(query)
        currency = result.scalar()
        return currency
    except Exception as e:
        print(e)
    finally:
        await session.close()


async def set__currency(user_id: int, currency: schemas.CurrencyChangeSchema, session: AsyncSession = async_session_maker()):
    try:
        await check_user_exists(user_id=user_id)
        await check_currency_in_list(currency=currency.name)
        wallet = await get__wallet(user_id=user_id, session=session)
        stmt = update(Currency).values(**currency.model_dump()).where(
            (Currency.wallet_id == wallet.id) & (Currency.name == currency.name)
        )
        await session.execute(stmt)
        await session.commit()
    except Exception as e:
        print(e)
    finally:
        await session.close()


async def set__balance(user_id: int, balance: schemas.BalanceChangeSchema, session: AsyncSession = async_session_maker()):
    try:
        await check_user_exists(user_id=user_id)
        await set__currency(user_id=user_id, currency=balance, session=session)
        return {"message": "Balance successfully set/changed."}
    except HTTPException as e:
        return e
    except Exception as e:
        print(e)
    finally:
        await session.close()


async def get__balance(user_id: int, session: AsyncSession = async_session_maker()):
    try:
        wallet = await get__wallet(user_id=user_id, session=session)
        balance = await session.execute(
            select(Currency.quantity).where((Currency.wallet_id == wallet.id) & (Currency.name == "USDT")))
        balance_value = balance.scalar()
        return balance_value
    except Exception as e:
        print(e)
    finally:
        await session.close()


async def get_current_price(currency: str):
    try:
        key = currency + "USDT"
        currency_data = redis_client.get(key).replace("'", "\"")
        data_dict = json.loads(currency_data)
        price = data_dict["o"]
        if price:
            return float(price)
        return {"message": "Error happened. (Probably coin doesn't exist)"}
    except Exception as e:
        print(e)


# Transaction services
async def create_transaction(wallet_id: int, transaction: dict, session: AsyncSession = async_session_maker()):
    try:
        stmt = insert(Transaction).values(wallet_id=wallet_id, **transaction)
        await session.execute(stmt)
        await session.commit()
    except Exception as e:
        print(e)
    finally:
        await session.close()


async def buy__currency(user_id: int, transaction: schemas.PurchaseCoinSchema, session: AsyncSession = async_session_maker()):
    try:
        await check_user_exists(user_id=user_id)
        transaction_dict = transaction.model_dump()
        t_currency = transaction_dict.get("currency", None).upper()
        c_quantity = transaction_dict.get("quantity", None)
        await check_quantity(quantity=c_quantity)

        price = await get_current_price(t_currency)
        await check_price_exists(price)

        transaction_dict["currency"] = t_currency
        transaction_dict["price"] = price
        balance = await get__balance(user_id=user_id, session=session)
        await check_balance(balance=balance, price=price, quantity=c_quantity)

        balance = balance - c_quantity * price
        currency_dict = {"name": t_currency, "quantity": c_quantity}
        wallet = await get__wallet(user_id=user_id, session=session)
        currency = await get__currency(wallet_id=wallet.id, currency=t_currency, session=session)
        if currency:
            currency_dict["quantity"] = currency.quantity + c_quantity
            await set__currency(user_id=user_id, currency=schemas.CurrencyChangeSchema(**currency_dict))
        else:
            currency_dict["wallet_id"] = wallet.id
            await create__currency(currency=schemas.CurrencyCreateSchema(**currency_dict))

        await create_transaction(wallet_id=wallet.id, transaction=transaction_dict, session=session)
        balance_dict = {"quantity": balance}
        await set__balance(user_id=user_id, balance=schemas.BalanceChangeSchema(**balance_dict), session=session)
        return {"message": f"{c_quantity} {t_currency} successfully purchased"}
    except HTTPException as e:
        return e
    except Exception as e:
        print(e)
    finally:
        await session.close()


async def sell__currency(user_id: int, transaction: schemas.SaleCoinSchema, session: AsyncSession = async_session_maker()):
    try:
        await check_user_exists(user_id=user_id)
        transaction_dict = transaction.model_dump()
        t_currency = transaction_dict.get("currency", None).upper()
        c_quantity = transaction_dict.get("quantity", None)
        await check_quantity(quantity=c_quantity)

        price = await get_current_price(t_currency)
        await check_price_exists(price)

        transaction_dict["currency"] = t_currency
        transaction_dict["price"] = price
        balance = await get__balance(user_id=user_id, session=session)

        balance = balance + c_quantity * price
        currency_dict = {"name": t_currency, "quantity": c_quantity}
        wallet = await get__wallet(user_id=user_id, session=session)
        currency = await get__currency(wallet_id=wallet.id, currency=t_currency, session=session)

        await check_currency_exist(currency=currency)
        await check_c_quantity_not_negative(currency=currency, sell_c_quantity=c_quantity)

        currency_dict["quantity"] = currency.quantity - c_quantity
        await set__currency(user_id=user_id, currency=schemas.CurrencyChangeSchema(**currency_dict))

        await create_transaction(wallet_id=wallet.id, transaction=transaction_dict, session=session)
        balance_dict = {"name": "USDT", "quantity": balance}
        await set__balance(user_id=user_id, balance=schemas.BalanceChangeSchema(**balance_dict))
        return {"message": f"{c_quantity} {t_currency} successfully sold"}
    except HTTPException as e:
        return e
    except Exception as e:
        print(e)
    finally:
        await session.close()


async def swap__currency(user_id: int, transaction: schemas.SwapCoinSchema, session: AsyncSession = async_session_maker()):
    try:
        await check_user_exists(user_id=user_id)
        transaction_dict = transaction.model_dump()
        t_currency = transaction_dict.get("currency", None).upper()
        t_currency_2 = transaction_dict.get("currency_2", None).upper()
        c_quantity = transaction_dict.get("quantity", None)
        await check_quantity(quantity=c_quantity)

        price_1 = await get_current_price(t_currency)
        price_2 = await get_current_price(t_currency_2)
        await check_price_exists(price_1)
        await check_price_exists(price_2)

        c_quantity_2 = round(c_quantity * price_1 / price_2, 2)

        transaction_dict["currency"] = t_currency
        transaction_dict["currency_2"] = t_currency_2
        transaction_dict["price"] = c_quantity_2
        currency_dict_1 = {"name": t_currency, "quantity": c_quantity}
        currency_dict_2 = {"name": t_currency_2, "quantity": c_quantity_2}

        wallet = await get__wallet(user_id=user_id, session=session)
        w_currency_1 = await get__currency(wallet_id=wallet.id, currency=t_currency)
        w_currency_2 = await get__currency(wallet_id=wallet.id, currency=t_currency_2)

        await check_currency_exist(currency=w_currency_1)
        await check_c_quantity_not_negative(currency=w_currency_1, sell_c_quantity=c_quantity)

        currency_dict_1["quantity"] = w_currency_1.quantity - c_quantity

        if w_currency_2:
            currency_dict_2["quantity"] = w_currency_2.quantity + c_quantity_2
            await set__currency(user_id=user_id, currency=schemas.CurrencyChangeSchema(**currency_dict_2))
        else:
            currency_dict_2["quantity"] = c_quantity_2
            currency_dict_2["wallet_id"] = wallet.id
            await create__currency(currency=schemas.CurrencyCreateSchema(**currency_dict_2))
        await set__currency(user_id=user_id, currency=schemas.CurrencyChangeSchema(**currency_dict_1))
        await create_transaction(wallet_id=wallet.id, transaction=transaction_dict, session=session)
        return {"message": f"{c_quantity} {t_currency} successfully swapped to {c_quantity_2} {t_currency_2}"}
    except HTTPException as e:
        return e
    except Exception as e:
        print(e)
    finally:
        await session.close()


# Redis
async def save_coin_data_to_redis(json_list):
    try:
        for json_data in json_list:
            if "USDT" not in json_data["s"]:
                continue
            event_time = json_data["E"]
            symbol = json_data["s"]
            history_key = f"{str(event_time)}_{symbol}"
            price_key = f"{str(symbol)}"
            redis_client.set(history_key, str(json_data), ex=CURRENCY_CACHE_TIME)
            redis_client.set(price_key, str(json_data))
    finally:
        redis_client.close()


async def get_currency_data_from_redis(currency: str, websocket: WebSocket):
    try:
        for key in redis_client.scan_iter(f"*_{currency}", count=100):
            value = redis_client.get(key)
            data = {key: value}
            await websocket.send_json(str(data))

        while websocket.client_state != WebSocketState.DISCONNECTED:
            for key in redis_client.scan_iter(f"{currency}", count=100):
                value = redis_client.get(key)
                time = json.loads(str(value).replace("'", "\""))["E"]
                key = f"{time}_{key}"
                data = {key: value}
                await websocket.send_json(str(data))
                await asyncio.sleep(1)
    except RedisError as e:
        print(f"Error while getting coin data: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        await websocket.close()


# BinanceAPI services
async def get_currency_data():
    url = BINANCE_WEBSOCKET_ALL_COINS_URL

    try:
        async with websockets.connect(uri=url) as ws:
            while True:
                data = await ws.recv()
                json_list = json.loads(data)
                await save_coin_data_to_redis(json_list)
                await asyncio.sleep(1)
    except Exception as e:
        print(f"Error while getting coin data: {e}")


async def get_history_prices(websocket: WebSocket, coin_name: str, interval: str):
    uri = BINANCE_WEBSOCKET_URL
    async with (websockets.connect(uri=f"{uri}{coin_name}@kline_{interval}") as ws):
        while True:
            data = await ws.recv()
            await websocket.send_json(data)
            await asyncio.sleep(1)


# OtherCryptaAPI services
def get_history_prices_coincap(interval: str = "d1"):
    url = f"https://api.coincap.io/v2/assets/bitcoin/history?interval={interval}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data['data']
    return response.status_code


def get_history_prices_gecko(symbol: str = "bitcoin", vs_currency: str = "usd",
                                days: str | int = "90", interval: str = "daily"):
    url = f'https://api.coingecko.com/api/v3/coins/{symbol}/market_chart'
    params = {
        'vs_currency': vs_currency,
        'days': days,
        'interval': interval,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    return response.status_code
