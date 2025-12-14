from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Order, PaymentStatus, Table
from app.schemas.tables import TableOut
from app.schemas.types import TableStatus

router = APIRouter(prefix="/api", tags=["tables"])


@router.get("/tables", response_model=list[TableOut])
def get_tables(db: Session = Depends(get_db)):
    tables = list(db.scalars(select(Table).where(Table.is_active == True).order_by(Table.id)))

    # For each table: open (unpaid) total
    open_totals = dict(
        db.execute(
            select(Order.table_id, func.coalesce(func.sum(Order.total), 0).label("total"))
            .where(Order.payment_status == PaymentStatus.PENDING, Order.table_id.is_not(None))
            .group_by(Order.table_id)
        ).all()
    )

    out: list[TableOut] = []
    for t in tables:
        total = int(open_totals.get(t.id, 0))
        status = TableStatus.OCCUPIED if total > 0 else TableStatus.EMPTY
        out.append(TableOut(id=t.id, name=t.name, status=status, total_amount=total if total > 0 else None))
    return out
