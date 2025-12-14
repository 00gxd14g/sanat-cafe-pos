from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.settings import AppSettingsIn, AppSettingsOut, PrinterSettingsIn, PrinterSettingsOut
from app.services.audit_service import AuditService
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/api", tags=["settings"])
service = SettingsService()
audit = AuditService()


@router.get("/settings/app", response_model=AppSettingsOut)
def get_app_settings(db: Session = Depends(get_db)):
    s = service.get_app_settings(db)
    return s.__dict__


@router.put("/settings/app", response_model=AppSettingsOut)
def put_app_settings(payload: AppSettingsIn, db: Session = Depends(get_db)):
    service.upsert(
        db,
        {
            "PRINT_STRATEGY": payload.print_strategy,
            "PRINT_MODE": payload.print_mode,
            "PRINT_OUTPUT_DIR": payload.print_output_dir,
            "PRINTER_KITCHEN_NAME": payload.printer_kitchen_name,
            "PRINTER_CUSTOMER_NAME": payload.printer_customer_name,
            "KITCHEN_SHOW_PRICES": "true" if payload.kitchen_show_prices else "false",
            "CUSTOMER_SHOW_PRICES": "true" if payload.customer_show_prices else "false",
            "QZ_ENCODING": payload.qz_encoding,
        },
    )
    s = service.get_app_settings(db)
    audit.log(db, action="UPDATE", entity="SETTINGS", entity_id="app", message="App settings updated", payload=s.__dict__)
    return s.__dict__


@router.get("/settings/printers", response_model=PrinterSettingsOut)
def get_printers(db: Session = Depends(get_db)):
    s = service.get_app_settings(db)
    return {"kitchen_printer_name": s.printer_kitchen_name, "customer_printer_name": s.printer_customer_name}


@router.put("/settings/printers", response_model=PrinterSettingsOut)
def put_printers(payload: PrinterSettingsIn, db: Session = Depends(get_db)):
    service.upsert(
        db,
        {
            "PRINTER_KITCHEN_NAME": payload.kitchen_printer_name,
            "PRINTER_CUSTOMER_NAME": payload.customer_printer_name,
        },
    )
    s = service.get_app_settings(db)
    audit.log(
        db,
        action="UPDATE",
        entity="SETTINGS",
        entity_id="printers",
        message="Printer names updated",
        payload={"kitchen": s.printer_kitchen_name, "customer": s.printer_customer_name},
    )
    return {"kitchen_printer_name": s.printer_kitchen_name, "customer_printer_name": s.printer_customer_name}
