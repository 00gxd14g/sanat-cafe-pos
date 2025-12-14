from __future__ import annotations

from pydantic import BaseModel


class AppSettingsOut(BaseModel):
    print_strategy: str
    print_mode: str
    print_output_dir: str
    printer_kitchen_name: str
    printer_customer_name: str
    kitchen_show_prices: bool
    customer_show_prices: bool
    qz_encoding: str


class AppSettingsIn(BaseModel):
    print_strategy: str
    print_mode: str
    print_output_dir: str
    printer_kitchen_name: str
    printer_customer_name: str
    kitchen_show_prices: bool
    customer_show_prices: bool
    qz_encoding: str


class PrinterSettingsOut(BaseModel):
    kitchen_printer_name: str
    customer_printer_name: str


class PrinterSettingsIn(BaseModel):
    kitchen_printer_name: str
    customer_printer_name: str
