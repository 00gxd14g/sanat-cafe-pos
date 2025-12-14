from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.timezone import now_local
from app.db.session import get_db
from app.models.order import Order, OrderItem
from app.models.print_job import PrintJob
from app.schemas.orders import PrintJobOut
from app.services.escpos import PrintLineItem, render_receipt_commands
from app.services.settings_service import SettingsService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/print", tags=["print"])
audit = AuditService()


def _build_payload_for_order(db: Session, *, order_id: int, job_type: str) -> dict:
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    items = list(
        db.execute(select(OrderItem).where(OrderItem.order_id == order_id).order_by(OrderItem.id.asc())).scalars()
    )
    if not items:
        raise HTTPException(status_code=400, detail="Order has no items")

    app_settings = SettingsService().get_app_settings(db)
    printer_hint = app_settings.printer_kitchen_name if job_type == "KITCHEN" else app_settings.printer_customer_name
    show_prices = app_settings.kitchen_show_prices if job_type == "KITCHEN" else app_settings.customer_show_prices
    title = "MUTFAK" if job_type == "KITCHEN" else "MUSTERI"
    table_label = f"Masa {order.table_id}" if order.table_id is not None else "Paket Servis"

    print_items = [
        PrintLineItem(
            name=it.name_snapshot,
            qty=int(it.qty),
            unit_price=float(it.unit_price_snapshot),
            line_total=float(it.line_total),
        )
        for it in items
    ]

    raw = render_receipt_commands(
        title=title,
        created_at=order.created_at,
        table_label=table_label,
        items=print_items,
        total=float(order.total),
        show_prices=show_prices,
    )

    return {
        "printerHint": printer_hint,
        "encoding": app_settings.qz_encoding,
        "raw": raw,
    }


@router.post("/payload")
def print_payload(body: dict, db: Session = Depends(get_db)):
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Invalid body")

    if "printJobId" in body:
        try:
            job_id = int(body["printJobId"])
        except Exception:
            raise HTTPException(status_code=400, detail="printJobId must be an integer")

        job = db.get(PrintJob, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Print job not found")
        return _build_payload_for_order(db, order_id=int(job.order_id), job_type=str(job.job_type))

    if "orderId" in body:
        try:
            order_id = int(body["orderId"])
        except Exception:
            raise HTTPException(status_code=400, detail="orderId must be an integer")
        job_type = str(body.get("type") or "CUSTOMER").upper()
        if job_type == "RECEIPT":
            job_type = "CUSTOMER"
        if job_type not in {"KITCHEN", "CUSTOMER"}:
            raise HTTPException(status_code=400, detail="type must be KITCHEN|CUSTOMER|receipt")
        return _build_payload_for_order(db, order_id=order_id, job_type=job_type)

    raise HTTPException(status_code=400, detail="Provide printJobId or orderId")


@router.post("/jobs", response_model=PrintJobOut)
def create_print_job(body: dict, db: Session = Depends(get_db)):
    try:
        order_id = int((body or {}).get("order_id"))
    except Exception:
        raise HTTPException(status_code=400, detail="order_id is required")

    job_type = str((body or {}).get("type") or "CUSTOMER").upper()
    if job_type == "RECEIPT":
        job_type = "CUSTOMER"
    if job_type not in {"KITCHEN", "CUSTOMER"}:
        raise HTTPException(status_code=400, detail="type must be KITCHEN|CUSTOMER|receipt")

    payload = _build_payload_for_order(db, order_id=order_id, job_type=job_type)
    created_at = db.get(Order, order_id).created_at  # already validated by _build_payload_for_order
    app_settings = SettingsService().get_app_settings(db)
    job = PrintJob(
        order_id=order_id,
        job_type=job_type,
        printer_name=payload["printerHint"] or "",
        payload_raw=("".join(payload["raw"])).encode(payload.get("encoding") or settings.qz_encoding, errors="replace"),
        status="PENDING" if (app_settings.print_strategy or "").lower() != "qz" else "CLIENT_PENDING",
        attempts=0,
        created_at=created_at,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"id": job.id, "type": job.job_type, "status": job.status}


@router.post("/jobs/{job_id}/ack")
def ack_print_job(job_id: int, body: dict, db: Session = Depends(get_db)):
    job = db.get(PrintJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Print job not found")

    status = str((body or {}).get("status") or "").upper()
    if status not in {"SENT", "PRINTED", "ERROR"}:
        raise HTTPException(status_code=400, detail="status must be SENT|PRINTED|ERROR")

    if status == "SENT":
        job.status = "PRINTING"
    elif status == "PRINTED":
        job.status = "PRINTED"
        job.printed_at = now_local()
        job.last_error = None
    else:
        job.status = "FAILED"
        job.attempts = int(job.attempts or 0) + 1
        job.last_error = str((body or {}).get("error") or "")

    db.add(job)
    db.commit()
    audit.log(
        db,
        action="UPDATE",
        entity="PRINT_JOB",
        entity_id=str(job.id),
        message=f"Print job ack: {status}",
        payload={"status": status, "error": (body or {}).get("error")},
    )
    return {"ok": True}


@router.post("/jobs/{job_id}/retry")
def retry_print_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(PrintJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Print job not found")
    job.status = "PENDING"
    job.last_error = None
    db.add(job)
    db.commit()
    audit.log(db, action="UPDATE", entity="PRINT_JOB", entity_id=str(job.id), message="Print job retry", payload=None)
    return {"ok": True}
