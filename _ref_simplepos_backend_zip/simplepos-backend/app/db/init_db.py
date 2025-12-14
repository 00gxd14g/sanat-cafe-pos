from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.timezone import now_local
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models import Category, Product, Table
from app.models.setting import Setting
from app.services.settings_service import CUSTOMER_KEY, KITCHEN_KEY


def create_all() -> None:
    Base.metadata.create_all(bind=engine)


def seed_if_empty() -> None:
    db: Session = SessionLocal()
    try:
        # Tables
        has_tables = db.scalar(select(Table.id).limit(1))
        if not has_tables:
            db.add_all([Table(name=f"Masa {i}") for i in range(1, 21)])

        # Categories
        has_cats = db.scalar(select(Category.id).limit(1))
        if not has_cats:
            categories = [
                ("Tost Çeşitleri", 10),
                ("Sandviçler", 20),
                ("İçecekler", 30),
                ("Çorbalar (Her Gün)", 40),
                ("Kahvaltılar", 50),
                ("Ek Kahvaltı Tercihleri", 60),
                ("Salatalar", 70),
                ("Tatlılar", 80),
            ]
            for name, sort_order in categories:
                db.add(Category(name=name, sort_order=sort_order))

        db.flush()

        # Products
        has_products = db.scalar(select(Product.id).limit(1))
        if not has_products:
            cat_map = {c.name: c.id for c in db.scalars(select(Category)).all()}

            def add(name: str, price: int, cat: str, active: bool = True, image_url: str | None = None):
                db.add(
                    Product(
                        category_id=cat_map[cat],
                        name=name,
                        price=price,
                        is_active=active,
                        image_url=image_url,
                    )
                )

            # Tost Çeşitleri
            add("Aria Karışık Tost", 120, "Tost Çeşitleri")
            add("Legato Sucuklu Tost", 100, "Tost Çeşitleri")
            add("Vibrato Kaşarlı Tost", 100, "Tost Çeşitleri")
            add("Forte Kavurmalı Tost", 150, "Tost Çeşitleri")

            # Sandviçler
            add("Brass Sosisli Patso", 140, "Sandviçler")
            add("Tenor Sucuklu Patso", 150, "Sandviçler")
            add("Kralın Eli Sandviç (Patatesli – Kuru)", 120, "Sandviçler")
            add("Contrabass Köfte Ekmek", 200, "Sandviçler")

            # İçecekler
            add("Çay", 20, "İçecekler")
            add("Türk Kahvesi (50)", 50, "İçecekler")
            add("Türk Kahvesi (70)", 70, "İçecekler")
            add("Soda / Sade Soda", 30, "İçecekler")
            add("Meyveli Soda", 40, "İçecekler")
            add("Limonata", 50, "İçecekler")
            add("Şalgam", 30, "İçecekler")
            add("Nescafe", 60, "İçecekler")
            add("Ayran", 40, "İçecekler")
            # TBD prices -> inactive until configured
            add("Cola", 0, "İçecekler", active=False)
            add("Fanta", 0, "İçecekler", active=False)
            add("Bitki Çay Çeşitleri", 0, "İçecekler", active=False)

            # Çorbalar (Her Gün)
            add("Ezogelin", 100, "Çorbalar (Her Gün)")
            add("Şehriyeli Tavuk", 100, "Çorbalar (Her Gün)")
            add("Tarhana", 100, "Çorbalar (Her Gün)")
            add("Kelle Paça", 100, "Çorbalar (Her Gün)")
            add("Mercimek", 100, "Çorbalar (Her Gün)")

            # Kahvaltılar
            add("Senfoni Organik Kahvaltı (Minimum 2 Kişilik)", 350, "Kahvaltılar")
            add("Allegro Hızlı Kahvaltı", 0, "Kahvaltılar", active=False)  # TBD

            # Ek Kahvaltı Tercihleri
            add("Trio Menemen", 170, "Ek Kahvaltı Tercihleri")
            add("Solfej Omlet", 100, "Ek Kahvaltı Tercihleri")
            add("Tenor Sucuklu Yumurta", 220, "Ek Kahvaltı Tercihleri")
            add("Bariton Kavurmalı Yumurta", 270, "Ek Kahvaltı Tercihleri")
            add("Legato Patatesli Yumurta", 170, "Ek Kahvaltı Tercihleri")
            add("Crescendo Karışık Menemen", 220, "Ek Kahvaltı Tercihleri")
            add("Ritmo Doğan Halkası (6'lı)", 24, "Ek Kahvaltı Tercihleri")

            # Salatalar
            add("Allegro Ton Balıklı Salata", 300, "Salatalar")
            add("Akustik Çoban Salata", 120, "Salatalar")
            add("Sahil Ezgisi Mersin Salatası", 120, "Salatalar")
            add("Staccato Makarna Salatası", 120, "Salatalar")
            add("Dolce Rus Salatası", 120, "Salatalar")
            add("Maestro Tavuklu Sezar", 350, "Salatalar")

            # Tatlılar
            add("Armoni Limonlu Kek", 40, "Tatlılar")
            add("Vivaldi Portakallı Revani", 40, "Tatlılar")
            add("Presto Trileçe", 60, "Tatlılar")
            add("Serenat Tiramisu", 60, "Tatlılar")
            add("Nota Islak Kek", 50, "Tatlılar")
            add("Opera Aşçıdan Pasta", 50, "Tatlılar")
            add("Virtüöz Ekler (Büyük)", 80, "Tatlılar")

        # Default printer settings in DB (so UI can override later)
        if not db.get(Setting, KITCHEN_KEY):
            db.add(Setting(key=KITCHEN_KEY, value=settings.PRINTER_KITCHEN_NAME))
        if not db.get(Setting, CUSTOMER_KEY):
            db.add(Setting(key=CUSTOMER_KEY, value=settings.PRINTER_CUSTOMER_NAME))

        db.commit()
    finally:
        db.close()
