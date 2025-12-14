from __future__ import annotations

from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: int
    created_at: str
    action: str
    entity: str
    entity_id: str
    message: str
    payload_json: str | None = None

