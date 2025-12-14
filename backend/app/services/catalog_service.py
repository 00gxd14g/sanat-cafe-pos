from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product


class CatalogService:
    def list_categories(self, db: Session) -> list[Category]:
        return list(
            db.execute(
                select(Category).where(Category.is_active.is_(True)).order_by(Category.sort_order.asc(), Category.name.asc())
            ).scalars()
        )

    def list_products(self, db: Session, *, category_id: int | None) -> list[Product]:
        stmt = select(Product).where(Product.is_active.is_(True))
        if category_id is not None:
            stmt = stmt.where(Product.category_id == category_id)
        stmt = stmt.where(Product.price.is_not(None), Product.price > 0)
        return list(db.execute(stmt.order_by(Product.name.asc())).scalars())
