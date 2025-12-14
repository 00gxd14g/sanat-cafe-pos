from __future__ import annotations

from pydantic import BaseModel


class CategoryOut(BaseModel):
    id: int
    name: str


class ProductOut(BaseModel):
    id: int
    category_id: int
    name: str
    price: float
    image: str | None = None


class CategoryIn(BaseModel):
    name: str
    sort_order: int = 0
    is_active: bool = True


class CategoryAdminOut(CategoryOut):
    sort_order: int
    is_active: bool


class ProductIn(BaseModel):
    category_id: int
    name: str
    price: float
    is_active: bool = True
    image_url: str | None = None
    sku: str | None = None


class ProductAdminOut(BaseModel):
    id: int
    category_id: int
    name: str
    price: float
    is_active: bool
    image_url: str | None = None
    sku: str | None = None
