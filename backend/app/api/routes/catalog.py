from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.catalog import CategoryAdminOut, CategoryIn, CategoryOut, ProductAdminOut, ProductIn, ProductOut
from app.services.catalog_service import CatalogService
from app.services.audit_service import AuditService
from app.models.category import Category
from app.models.product import Product
from sqlalchemy import select

router = APIRouter(prefix="/api", tags=["catalog"])
service = CatalogService()
audit = AuditService()


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    categories = service.list_categories(db)
    return [{"id": c.id, "name": c.name} for c in categories]


@router.get("/products", response_model=list[ProductOut])
def list_products(category_id: int | None = Query(default=None), db: Session = Depends(get_db)):
    products = service.list_products(db, category_id=category_id)
    return [
        {"id": p.id, "category_id": p.category_id, "name": p.name, "price": float(p.price), "image": p.image_url}
        for p in products
    ]


@router.get("/admin/categories", response_model=list[CategoryAdminOut])
def admin_list_categories(db: Session = Depends(get_db)):
    categories = list(db.execute(select(Category).order_by(Category.sort_order.asc(), Category.name.asc())).scalars())
    return [{"id": c.id, "name": c.name, "sort_order": c.sort_order, "is_active": c.is_active} for c in categories]


@router.post("/admin/categories", response_model=CategoryAdminOut)
def admin_create_category(payload: CategoryIn, db: Session = Depends(get_db)):
    c = Category(name=payload.name, sort_order=payload.sort_order, is_active=payload.is_active)
    db.add(c)
    db.commit()
    db.refresh(c)
    audit.log(db, action="CREATE", entity="CATEGORY", entity_id=str(c.id), message="Category created", payload=payload.model_dump())
    return {"id": c.id, "name": c.name, "sort_order": c.sort_order, "is_active": c.is_active}


@router.put("/admin/categories/{category_id}", response_model=CategoryAdminOut)
def admin_update_category(category_id: int, payload: CategoryIn, db: Session = Depends(get_db)):
    c = db.get(Category, category_id)
    if not c:
        raise HTTPException(status_code=404, detail="Category not found")
    c.name = payload.name
    c.sort_order = payload.sort_order
    c.is_active = payload.is_active
    db.add(c)
    db.commit()
    db.refresh(c)
    audit.log(db, action="UPDATE", entity="CATEGORY", entity_id=str(c.id), message="Category updated", payload=payload.model_dump())
    return {"id": c.id, "name": c.name, "sort_order": c.sort_order, "is_active": c.is_active}


@router.get("/admin/products", response_model=list[ProductAdminOut])
def admin_list_products(db: Session = Depends(get_db)):
    products = list(db.execute(select(Product).order_by(Product.id.asc())).scalars())
    return [
        {
            "id": p.id,
            "category_id": p.category_id,
            "name": p.name,
            "price": float(p.price),
            "is_active": p.is_active,
            "image_url": p.image_url,
            "sku": p.sku,
        }
        for p in products
    ]


@router.post("/admin/products", response_model=ProductAdminOut)
def admin_create_product(payload: ProductIn, db: Session = Depends(get_db)):
    p = Product(
        category_id=payload.category_id,
        name=payload.name,
        price=payload.price,
        is_active=payload.is_active,
        image_url=payload.image_url,
        sku=payload.sku,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    audit.log(db, action="CREATE", entity="PRODUCT", entity_id=str(p.id), message="Product created", payload=payload.model_dump())
    return {
        "id": p.id,
        "category_id": p.category_id,
        "name": p.name,
        "price": float(p.price),
        "is_active": p.is_active,
        "image_url": p.image_url,
        "sku": p.sku,
    }


@router.put("/admin/products/{product_id}", response_model=ProductAdminOut)
def admin_update_product(product_id: int, payload: ProductIn, db: Session = Depends(get_db)):
    p = db.get(Product, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    p.category_id = payload.category_id
    p.name = payload.name
    p.price = payload.price
    p.is_active = payload.is_active
    p.image_url = payload.image_url
    p.sku = payload.sku
    db.add(p)
    db.commit()
    db.refresh(p)
    audit.log(db, action="UPDATE", entity="PRODUCT", entity_id=str(p.id), message="Product updated", payload=payload.model_dump())
    return {
        "id": p.id,
        "category_id": p.category_id,
        "name": p.name,
        "price": float(p.price),
        "is_active": p.is_active,
        "image_url": p.image_url,
        "sku": p.sku,
    }
