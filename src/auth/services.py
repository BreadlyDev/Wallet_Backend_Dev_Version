from typing import Optional

from fastapi import Depends, Request
from fastapi_users import IntegerIDMixin, BaseUserManager, schemas, exceptions, models
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.mail_sender import send_email
from src.auth.models import User, Role
from src.auth.schemas import RoleCreateSchema
from src.auth.utilts import get_user_db
from src.config import SECRET
from src.database import async_session_maker
from src.wallet.services import create_wallet
from src.wallet.schemas import WalletCreateSchema


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")
        wallet_dict = {
            "user_id": user.id,
        }
        wallet_data = WalletCreateSchema(**wallet_dict)
        await create_wallet(wallet_data=wallet_data)

    async def on_after_forgot_password(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")
        await send_email(user.email, token)

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
        if user_dict.get("oauth_accounts") is not None:
            user_dict["is_verified"] = True
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        user_dict["role_id"] = 1

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


async def create_role(user_id: int, role_data: RoleCreateSchema, session: AsyncSession = async_session_maker()):
    async with session.begin():
        user_is_superuser = select(User.is_superuser).where(User.id == user_id).scalar_subquery()

        if not user_is_superuser:
            return

        stmt = insert(Role).values(**role_data.model_dump())
        await session.execute(stmt)
        await session.commit()


async def get_role(user_id: int, session: AsyncSession = async_session_maker()):
    async with session.begin():
        user_is_superuser = select(User.is_superuser).where(User.id == user_id).scalar_subquery()

        if not user_is_superuser:
            return

        query = select(Role)
        await session.execute(query)


# Only for DEVs
async def create_default_role(session: AsyncSession = async_session_maker()):
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