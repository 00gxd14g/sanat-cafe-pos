from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.tables import TableOut
from app.services.order_service import OrderService

router = APIRouter(prefix="/api", tags=["tables"])
service = OrderService()


@router.get("/tables", response_model=list[TableOut])
def list_tables(db: Session = Depends(get_db)):
    return service.list_tables_for_dashboard(db)

