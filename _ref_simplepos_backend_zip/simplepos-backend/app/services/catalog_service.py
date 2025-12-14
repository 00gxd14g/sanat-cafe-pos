from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category, Product


def list_categories(db: Session) -> list[Category]:
    return list(db.scalars(select(Category).where(Category.is_active == True).order_by(Category.sort_order, Category.name)))


def list_products(db: Session, category_id: int | None = None) -> list[Product]:
    stmt = select(Product).where(Product.is_active == True)
    if category_id:
        stmt = stmt.where(Product.category_id == category_id)
    stmt = stmt.order_by(Product.category_id, Product.name)
    return list(db.scalars(stmt))
