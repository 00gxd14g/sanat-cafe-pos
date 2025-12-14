from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.timezone import now_local
from app.models.audit_log import AuditLog


class AuditService:
    def log(
        self,
        db: Session,
        *,
        action: str,
        entity: str,
        entity_id: str = "",
        message: str = "",
        payload: Any | None = None,
    ) -> None:
        row = AuditLog(
            created_at=now_local(),
            action=action,
            entity=entity,
            entity_id=str(entity_id or ""),
            message=message,
            payload_json=json.dumps(payload, ensure_ascii=False) if payload is not None else None,
        )
        db.add(row)
        db.commit()

    def list(self, db: Session, *, limit: int = 200) -> list[AuditLog]:
        limit = max(1, min(int(limit), 1000))
        return list(db.execute(select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)).scalars())

