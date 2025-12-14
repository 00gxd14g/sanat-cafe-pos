from __future__ import annotations

from pydantic import BaseModel


class PrintJobDebugOut(BaseModel):
    id: int
    order_id: int
    job_type: str
    printer_name: str
    status: str
    attempts: int
    last_error: str | None = None

