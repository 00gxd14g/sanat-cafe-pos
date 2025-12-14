from __future__ import annotations

from pydantic import BaseModel
from app.schemas.types import TableStatus


class TableOut(BaseModel):
    id: int
    name: str
    status: TableStatus
    total_amount: int | None = None
