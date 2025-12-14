from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Setting

KITCHEN_KEY = "PRINTER_KITCHEN_NAME"
CUSTOMER_KEY = "PRINTER_CUSTOMER_NAME"


def _get(db: Session, key: str, default: str) -> str:
    row = db.scalar(select(Setting).where(Setting.key == key))
    return row.value if row else default


def get_printer_settings(db: Session) -> tuple[str, str]:
    return (
        _get(db, KITCHEN_KEY, settings.PRINTER_KITCHEN_NAME),
        _get(db, CUSTOMER_KEY, settings.PRINTER_CUSTOMER_NAME),
    )


def set_printer_settings(db: Session, kitchen: str, customer: str) -> None:
    for key, value in [(KITCHEN_KEY, kitchen), (CUSTOMER_KEY, customer)]:
        row = db.get(Setting, key)
        if row:
            row.value = value
        else:
            db.add(Setting(key=key, value=value))
    db.commit()
