from __future__ import annotations

from pydantic import BaseModel, Field


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    price: float | None = None


class OrderCreateIn(BaseModel):
    table_id: int
    payment_status: str  # PAID|PENDING
    items: list[OrderItemIn] = Field(min_length=1)


class PrintJobOut(BaseModel):
    id: int
    type: str
    status: str


class OrderCreateOut(BaseModel):
    success: bool
    message: str
    order_id: int
    total: float
    print_jobs: list[PrintJobOut]


class OrderItemOut(BaseModel):
    product_id: int
    name: str
    quantity: int
    unit_price: float
    line_total: float


class OrderOut(BaseModel):
    id: int
    table_id: int | None
    status: str
    payment_status: str
    total: float
    created_at: str
    paid_at: str | None = None
    items: list[OrderItemOut]


class OrderUpdateIn(BaseModel):
    status: str | None = None
    payment_status: str | None = None
