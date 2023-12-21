from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse

from src.config import SECRET
from fastapi import FastAPI

middleware_app = FastAPI()

SECRET_KEY = SECRET or None

if SECRET_KEY is None:
    raise 'Missing SECRET_KEY'
middleware_app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


@middleware_app.get('/')
def test():
    return JSONResponse({'message': 'auth_app'})
