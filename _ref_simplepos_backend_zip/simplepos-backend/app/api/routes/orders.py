from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.orders import OrderCreateResponse, OrderPayloadIn, PrintJobOut
from app.services.order_service import OrderError, create_order_and_queue_prints

router = APIRouter(prefix="/api", tags=["orders"])


@router.post("/orders", response_model=OrderCreateResponse)
def create_order(payload: OrderPayloadIn, db: Session = Depends(get_db)):
    try:
        order, jobs = create_order_and_queue_prints(
            db,
            table_id=payload.table_id,
            payment_status=payload.payment_status,
            items_in=[it.model_dump() for it in payload.items],
        )
    except OrderError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return OrderCreateResponse(
        success=True,
        message="Order created. Print jobs queued.",
        order_id=order.id,
        total=int(order.total),
        print_jobs=[PrintJobOut(id=j.id, type=j.job_type.value, status=j.status.value) for j in jobs],
    )
