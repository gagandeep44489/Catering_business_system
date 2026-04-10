from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6)


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class MenuBase(BaseModel):
    name: str
    category: str
    price: float = Field(gt=0)
    description: str = ""


class MenuCreate(MenuBase):
    pass


class MenuUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    price: float | None = Field(default=None, gt=0)
    description: str | None = None


class MenuOut(MenuBase):
    id: int

    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    menu_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    event_type: Literal["Wedding", "Party", "Corporate"]
    guests: int = Field(gt=0)
    event_date: datetime
    items: list[OrderItemCreate]


class OrderItemOut(BaseModel):
    id: int
    menu_id: int
    quantity: int
    menu_name: str
    menu_price: float
    line_total: float


class OrderOut(BaseModel):
    id: int
    user_id: int
    customer_name: str
    total_price: float
    status: str
    event_type: str
    guests: int
    event_date: datetime
    created_at: datetime
    items: list[OrderItemOut]


class OrderStatusUpdate(BaseModel):
    status: Literal["Pending", "Confirmed", "Completed"]
