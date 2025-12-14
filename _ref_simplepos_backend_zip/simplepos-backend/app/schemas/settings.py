from __future__ import annotations

from pydantic import BaseModel


class PrinterSettingsOut(BaseModel):
    kitchen_printer_name: str
    customer_printer_name: str


class PrinterSettingsIn(BaseModel):
    kitchen_printer_name: str
    customer_printer_name: str
