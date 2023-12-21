from fastapi_users import schemas
from pydantic import BaseModel, EmailStr


class UserRead(schemas.BaseUser[int]):
    id: int
    email: EmailStr
    firstname: str
    lastname: str
    role_id: int
    is_active: bool
    is_superuser: bool
    is_verified: bool

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    firstname: str
    lastname: str
    password: str
    role_id: int = 1
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserUpdate(schemas.BaseUserUpdate):
    pass


class RoleCreateSchema(BaseModel):
    name: str
    permissions: dict

