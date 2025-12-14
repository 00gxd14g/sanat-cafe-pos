from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.catalog import CategoryOut, ProductOut
from app.services.catalog_service import list_categories, list_products

router = APIRouter(prefix="/api", tags=["catalog"])


@router.get("/categories", response_model=list[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    cats = list_categories(db)
    return [CategoryOut(id=c.id, name=c.name) for c in cats]


@router.get("/products", response_model=list[ProductOut])
def get_products(
    category_id: int | None = Query(default=None, description="Filter by category id"),
    db: Session = Depends(get_db),
):
    products = list_products(db, category_id=category_id)
    return [
        ProductOut(
            id=p.id,
            category_id=p.category_id,
            name=p.name,
            price=int(p.price),
            image=p.image_url,
        )
        for p in products
    ]
