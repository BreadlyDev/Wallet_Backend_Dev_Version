import asyncio

import uvicorn

from fastapi import FastAPI
from redis import RedisError
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

from src.auth.routers import auth_router
from src.wallet.services import get_history_prices, WebSocket, get_currency_data, get_currency_data_from_redis
from src.wallet.routers import wallet_router

app = FastAPI(
    title="Crypta"
)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "127.0.0.1:8080",
    "127.0.0.1:61033",
    "127.0.0.1:61034",
    "*",
]

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


@app.websocket("/history/")
async def websocket_endpoint(websocket: WebSocket, coin_name: str, interval: str):
    await websocket.accept()
    await get_history_prices(websocket=websocket, coin_name=coin_name, interval=interval)


@app.websocket("/ws/coin/price/")
async def get_currency_data_(currency: str, websocket: WebSocket):
    await websocket.accept()
    await get_currency_data_from_redis(currency=currency, websocket=websocket)


@app.get("/coin/price/get/", tags=["API"])
def read_root(currency: str):
    return HTMLResponse(
        f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>WebSocket Example</title>
            </head>
            <body>
                <h1>WebSocket Example</h1>
                <ol id='tickerList'></ol>
                <script>
                try {{
                    var ws = new WebSocket(`ws://127.0.0.1:8080/ws/coin/price/?currency={currency}`);
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


async def startup_event():
    print("Server is starting")


@app.on_event("startup")
async def on_startup():
    try:
        asyncio.create_task(get_currency_data())
    except asyncio.TimeoutError as e:
        print(e)
    except RedisError as e:
        print(e)

if __name__ == "__main__":
    uvicorn.run(app, port=8080, reload=True)
