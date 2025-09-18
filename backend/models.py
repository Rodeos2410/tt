from sqlmodel import SQLModel, Field
from typing import Optional
## Модели только! Не импортировать FastAPI/app/router здесь


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str
    blocked: bool = False
    balance: float = 0.0


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    price: float
    owner_id: Optional[int] = None
    file_url: Optional[str] = None


class Purchase(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    buyer_id: int
    product_id: int
    qty: int = 1
    total_price: float = 0.0


class UserCreate(SQLModel):
    username: str
    email: str
    password: str
    balance: Optional[float] = 0.0


class UserLogin(SQLModel):
    email: str
    password: str


class ProductCreate(SQLModel):
    title: str
    description: str
    price: float
    file_url: Optional[str] = None


## Здесь не должно быть app, router, импортов FastAPI, маршрутов и бизнес-логики
