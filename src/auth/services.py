from datetime import datetime, timedelta
from typing import Optional, Annotated, Union

from fastapi import Depends, Request, Form, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import IntegerIDMixin, BaseUserManager, schemas, exceptions, models
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from pydantic import EmailStr
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from passlib.context import CryptContext
import jwt

from src.auth.mail_sender import send_email
from src.auth.models import User, Role
from src.auth.schemas import RoleCreateSchema, UserCreate, LoginSchema
from src.auth.utilts import get_user_db
from src.config import SECRET
from src.database import async_session_maker
from src.wallet.services import create__wallet
from src.wallet.schemas import WalletCreateSchema

SECRET_KEY = SECRET
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 1


class CustomOAuth2PasswordRequestForm(OAuth2PasswordRequestForm):
    def __init__(
            self,
            *,
            email: Annotated[
                    EmailStr,
                    Form(),
            ],
            grant_type: Annotated[
                Union[str, None],
                Form(pattern="password"),
            ] = None,
            username: Annotated[
                str,
                Form(),
            ] = None,
            password: Annotated[
                str,
                Form(),
            ],
            scope: Annotated[
                str,
                Form(),
            ] = "",
            client_id: Annotated[
                Union[str, None],
                Form()
            ] = None,
            client_secret: Annotated[
                Union[str, None],
                Form()
            ] = None
            ):
        self.email = email
        super().__init__(grant_type=grant_type, username=username, password=password,
                         scope=scope, client_id=client_id, client_secret=client_secret)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")
        wallet_dict = {"user_id": user.id}
        wallet_data = WalletCreateSchema(**wallet_dict)
        await create__wallet(wallet_data=wallet_data)

    async def on_after_forgot_password(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")
        await send_email(user.email, token)
        return {"message": "Please check your email"}

    async def create(
            self,
            user_create: schemas.UC,
            safe: bool = False,
            request: Optional[Request] = None,
    ) -> models.UP:

        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        if user_dict.get("oauth_accounts"):
            user_dict["is_verified"] = True

        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        user_dict["role_id"] = 1

        created_user = await self.user_db.create(user_dict)
        await self.on_after_register(created_user, request)

        return created_user

    async def authenticate(
            self, credentials: CustomOAuth2PasswordRequestForm,
    ) -> Optional[models.UP]:

        try:
            user = await self.get_by_email(str(credentials.email))
        except exceptions.UserNotExists:

            self.password_helper.hash(credentials.password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        if not verified:
            return None

        if updated_password_hash is not None:
            await self.user_db.update(user, {"hashed_password": updated_password_hash})

        return user


async def check_user_exist(user: User):
    if not user:
        raise HTTPException(status_code=400, detail={"message": "User not found"})


async def check_user_is_verified(user: User):
    if not user.is_verified:
        raise HTTPException(status_code=400, detail={"message": "User is not verified"})


async def get_user_by_email(email: EmailStr, session: AsyncSession = async_session_maker()):
    try:
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        user = result.scalar()
        await check_user_exist(user=user)
        return user
    except Exception as e:
        print(e)
    finally:
        await session.close()


async def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def register(user: UserCreate, session: AsyncSession = async_session_maker()):
    try:
        pwt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwt_context.hash(user.password)
        user_dict = user.model_dump()
        user_dict.pop("password")

        stmt = insert(User).values(hashed_password=hashed_password, **user_dict)
        await session.execute(stmt)
        await session.commit()

        token_data = {"sub": user.email}
        access_token = await create_access_token(token_data)

        return {"access_token": access_token, "token_type": "bearer"}, user_dict
    except HTTPException as e:
        return e
    except Exception as e:
        print(e)


async def login(login_data: LoginSchema, session: AsyncSession = async_session_maker()):
    try:
        email = login_data.email
        password = login_data.password
        user = await get_user_by_email(email=email, session=session)

        pwt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        if not pwt_context.verify(password, user.hashed_password):
            raise HTTPException(status_code=400, detail={"message": "Invalid credentials"})

        token_data = {"sub": user.email}
        access_token = await create_access_token(token_data)

        return {"access_token": access_token, "token_type": "bearer"}, user
    except HTTPException as e:
        return e
    except Exception as e:
        print(e)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


async def create__role(user_id: int, role_data: RoleCreateSchema, session: AsyncSession = async_session_maker()):
    async with session.begin():
        user_is_superuser = select(User.is_superuser).where(User.id == user_id).scalar_subquery()

        if not user_is_superuser:
            return

        stmt = insert(Role).values(**role_data.model_dump())
        await session.execute(stmt)
        await session.commit()


async def get__role(user_id: int, session: AsyncSession = async_session_maker()):
    async with session.begin():
        user_is_superuser = select(User.is_superuser).where(User.id == user_id).scalar_subquery()

        if not user_is_superuser:
            return

        query = select(Role)
        await session.execute(query)


# Only for DEVs
async def create__default__role(session: AsyncSession = async_session_maker()):
    async with session.begin():

        role_data = {
            "name": "user",
            "permissions": None
        }

        user_role = insert(Role).values(**role_data)
        role_data["name"] = "admin"
        admin_role = insert(Role).values(**role_data)

        await session.execute(user_role)
        await session.execute(admin_role)
        await session.commit()
        return {"message": "default roles added"}
