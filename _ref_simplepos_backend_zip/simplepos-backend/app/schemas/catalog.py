from __future__ import annotations

from pydantic import BaseModel, Field


class CategoryOut(BaseModel):
    id: int
    name: str


class ProductOut(BaseModel):
    id: int
    category_id: int
    name: str
    price: int
    image: str | None = None
