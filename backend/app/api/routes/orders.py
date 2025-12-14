from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.orders import OrderCreateIn, OrderCreateOut, OrderOut, OrderUpdateIn
from app.services.audit_service import AuditService
from app.services.order_service import OrderService

router = APIRouter(prefix="/api", tags=["orders"])
service = OrderService()
audit = AuditService()


@router.post("/orders", response_model=OrderCreateOut)
def create_order(payload: OrderCreateIn, db: Session = Depends(get_db)):
    try:
        order, jobs = service.create_order(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    audit.log(
        db,
        action="CREATE",
        entity="ORDER",
        entity_id=str(order.id),
        message="Order created",
        payload={"table_id": payload.table_id, "payment_status": payload.payment_status, "items": [it.model_dump() for it in payload.items]},
    )

    return {
        "success": True,
        "message": "Order created. Print jobs queued.",
        "order_id": order.id,
        "total": float(order.total),
        "print_jobs": [{"id": j.id, "type": j.job_type, "status": j.status} for j in jobs],
    }


@router.get("/orders", response_model=list[OrderOut])
def list_orders(payment_status: str | None = None, db: Session = Depends(get_db)):
    return service.list_orders(db, payment_status=payment_status)


@router.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    try:
        return service.get_order(db, order_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/orders/{order_id}", response_model=OrderOut)
def patch_order(order_id: int, payload: OrderUpdateIn, db: Session = Depends(get_db)):
    try:
        out = service.update_order(db, order_id, status=payload.status, payment_status=payload.payment_status)
        audit.log(
            db,
            action="UPDATE",
            entity="ORDER",
            entity_id=str(order_id),
            message="Order updated",
            payload=payload.model_dump(exclude_none=True),
        )
        return out
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
