from __future__ import annotations

from pydantic import BaseModel, Field


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1, le=999)
    price: int = Field(..., ge=0)  # sent by frontend but NOT trusted by backend


class OrderPayloadIn(BaseModel):
    table_id: int = Field(..., ge=0)
    payment_status: str = Field(..., pattern="^(PAID|PENDING)$")
    items: list[OrderItemIn] = Field(..., min_length=1)


class PrintJobOut(BaseModel):
    id: int
    type: str
    status: str


class OrderCreateResponse(BaseModel):
    success: bool
    message: str
    order_id: int
    total: int
    print_jobs: list[PrintJobOut]
