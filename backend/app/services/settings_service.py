from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings as env
from app.models.setting import Setting


@dataclass(frozen=True)
class AppSettings:
    print_strategy: str
    print_mode: str
    print_output_dir: str
    printer_kitchen_name: str
    printer_customer_name: str
    kitchen_show_prices: bool
    customer_show_prices: bool
    qz_encoding: str


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    v = value.strip().lower()
    if v in {"1", "true", "yes", "y", "on"}:
        return True
    if v in {"0", "false", "no", "n", "off"}:
        return False
    return default


class SettingsService:
    KEYS = {
        "PRINT_STRATEGY",
        "PRINT_MODE",
        "PRINT_OUTPUT_DIR",
        "PRINTER_KITCHEN_NAME",
        "PRINTER_CUSTOMER_NAME",
        "KITCHEN_SHOW_PRICES",
        "CUSTOMER_SHOW_PRICES",
        "QZ_ENCODING",
    }

    def get_all(self, db: Session) -> dict[str, str]:
        rows = db.execute(select(Setting).where(Setting.key.in_(sorted(self.KEYS)))).scalars().all()
        return {r.key: r.value for r in rows}

    def get_app_settings(self, db: Session) -> AppSettings:
        raw = self.get_all(db)

        return AppSettings(
            print_strategy=(raw.get("PRINT_STRATEGY") or env.print_strategy).lower(),
            print_mode=(raw.get("PRINT_MODE") or env.print_mode).lower(),
            print_output_dir=(raw.get("PRINT_OUTPUT_DIR") or env.print_output_dir),
            printer_kitchen_name=(raw.get("PRINTER_KITCHEN_NAME") or env.printer_kitchen_name),
            printer_customer_name=(raw.get("PRINTER_CUSTOMER_NAME") or env.printer_customer_name),
            kitchen_show_prices=_parse_bool(raw.get("KITCHEN_SHOW_PRICES"), env.kitchen_show_prices),
            customer_show_prices=_parse_bool(raw.get("CUSTOMER_SHOW_PRICES"), env.customer_show_prices),
            qz_encoding=(raw.get("QZ_ENCODING") or env.qz_encoding),
        )

    def upsert(self, db: Session, values: dict[str, str]) -> None:
        for key, value in values.items():
            if key not in self.KEYS:
                continue
            row = db.get(Setting, key)
            if row:
                row.value = value
            else:
                db.add(Setting(key=key, value=value))
        db.commit()

