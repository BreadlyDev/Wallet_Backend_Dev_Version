import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
#0auth
SECRET = os.environ.get("SECRET")

GOOGLE_CLIENT_ID = str(os.environ.get("GOOGLE_CLIENT_ID"))

GOOGLE_CLIENT_SECRET = str(os.environ.get("GOOGLE_CLIENT_SECRET"))

#Google mail sender API
MAIL_HOST = os.environ.get("MAIL_HOST")
MAIL_EMAIL = os.environ.get("MAIL_EMAIL")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
MAIL_PORT = os.environ.get("MAIL_PORT")

#Binance and other similar API
CURRENCY_URL = str(os.environ.get("CURRENCY_URL"))
USD_PRICES_URI = str(os.environ.get("USD_PRICES_URI"))
BINANCE_WEBSOCKET_URL = str(os.environ.get("BINANCE_WEBSOCKET_URL"))
BINANCE_WEBSOCKET_ALL_COINS_URL = str(os.environ.get("BINANCE_WEBSOCKET_ALL_COINS_URL"))

RS_HOST = str(os.environ.get("RS_HOST"))
RS_PORT = str(os.environ.get("RS_PORT"))

CURRENCY_CACHE_TIME = str(os.environ.get("CURRENCY_CACHE_TIME"))
