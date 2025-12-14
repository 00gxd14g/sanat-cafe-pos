from __future__ import annotations

from sqlalchemy import select

from app.db.session import SessionLocal, init_db
from app.models.category import Category
from app.models.product import Product
from app.models.setting import Setting
from app.models.table import Table


def create_all() -> None:
    init_db()


def seed_if_empty() -> None:
    """Seed minimal data if DB is empty (safe to call on startup)."""
    with SessionLocal() as db:
        if db.execute(select(Table.id).limit(1)).first() is None:
            db.add_all([Table(id=i, name=f"Masa {i}", is_active=True) for i in range(1, 21)])

        if db.execute(select(Category.id).limit(1)).first() is None:
            db.add_all(
                [
                    Category(id=1, name="Tost ?e?itleri", sort_order=1, is_active=True),
                    Category(id=2, name="Sandvi?ler", sort_order=2, is_active=True),
                    Category(id=3, name="??ecekler", sort_order=3, is_active=True),
                ]
            )

        if db.execute(select(Product.id).limit(1)).first() is None:
            db.add_all(
                [
                    Product(id=101, category_id=1, name="Kar???k Tost", price=120, is_active=True, image_url=None, sku="TST-001"),
                    Product(id=102, category_id=1, name="Sucuklu Tost", price=100, is_active=True, image_url=None, sku="TST-002"),
                    Product(id=201, category_id=2, name="Sosisli Patso", price=140, is_active=True, image_url=None, sku="SND-001"),
                    Product(id=301, category_id=3, name="?ay", price=20, is_active=True, image_url=None, sku="ICE-001"),
                    Product(id=302, category_id=3, name="T?rk Kahvesi", price=50, is_active=True, image_url=None, sku="ICE-002"),
                ]
            )

        for key, value in {
            "PRINT_STRATEGY": "server",
            "PRINT_MODE": "file",
            "PRINT_OUTPUT_DIR": "backend/prints",
            "PRINTER_KITCHEN_NAME": "",
            "PRINTER_CUSTOMER_NAME": "",
            "KITCHEN_SHOW_PRICES": "false",
            "CUSTOMER_SHOW_PRICES": "true",
            "QZ_ENCODING": "CP857",
        }.items():
            if db.get(Setting, key) is None:
                db.add(Setting(key=key, value=value))

        db.commit()
