from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr, field_validator


class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock: int
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int

    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Quantity must be greater than zero")
        return v


class OrderCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    shipping_address: str
    items: List[OrderItemCreate]


class OrderItemRead(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


class OrderRead(BaseModel):
    id: int
    created_at: datetime
    customer_name: str
    customer_email: EmailStr
    shipping_address: str
    status: str
    items: List[OrderItemRead]

    class Config:
        from_attributes = True

