from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.settings import PrinterSettingsIn, PrinterSettingsOut
from app.services.settings_service import get_printer_settings, set_printer_settings

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/printers", response_model=PrinterSettingsOut)
def get_printers(db: Session = Depends(get_db)):
    kitchen, customer = get_printer_settings(db)
    return PrinterSettingsOut(kitchen_printer_name=kitchen, customer_printer_name=customer)


@router.put("/printers", response_model=PrinterSettingsOut)
def set_printers(payload: PrinterSettingsIn, db: Session = Depends(get_db)):
    set_printer_settings(db, payload.kitchen_printer_name, payload.customer_printer_name)
    kitchen, customer = get_printer_settings(db)
    return PrinterSettingsOut(kitchen_printer_name=kitchen, customer_printer_name=customer)
