from __future__ import annotations

from pydantic import BaseModel


class ReportStatsOut(BaseModel):
    total_revenue: float
    total_orders: int
    total_items: int


class SalesDataOut(BaseModel):
    name: str
    value: float

