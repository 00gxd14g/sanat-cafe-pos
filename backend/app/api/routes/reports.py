from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.reports import ReportStatsOut, SalesDataOut
from app.services.reporting_service import get_daily_sales_data, get_daily_stats

router = APIRouter(prefix="/api", tags=["reports"])


def _parse_date(d: str | None) -> date:
    if not d:
        return datetime.now().date()
    return date.fromisoformat(d)


@router.get("/reports/daily/stats", response_model=ReportStatsOut)
def daily_stats(date_str: str | None = Query(default=None, alias="date"), db: Session = Depends(get_db)):
    d = _parse_date(date_str)
    return ReportStatsOut(**get_daily_stats(db, d))


@router.get("/reports/daily/sales", response_model=list[SalesDataOut])
def daily_sales(date_str: str | None = Query(default=None, alias="date"), db: Session = Depends(get_db)):
    d = _parse_date(date_str)
    return [SalesDataOut(**x) for x in get_daily_sales_data(db, d)]
