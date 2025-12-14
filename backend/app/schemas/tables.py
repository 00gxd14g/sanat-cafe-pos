from __future__ import annotations

from pydantic import BaseModel


class TableOut(BaseModel):
    id: int
    name: str
    status: str  # empty|occupied
    total_amount: float | None = None

