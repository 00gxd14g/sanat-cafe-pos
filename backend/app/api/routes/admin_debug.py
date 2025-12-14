from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.audit import AuditLogOut
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/admin", tags=["admin-debug"])
audit = AuditService()


@router.get("/audit", response_model=list[AuditLogOut])
def list_audit(limit: int = Query(default=200, ge=1, le=1000), db: Session = Depends(get_db)):
    rows = audit.list(db, limit=limit)
    return [
        {
            "id": r.id,
            "created_at": r.created_at.isoformat(),
            "action": r.action,
            "entity": r.entity,
            "entity_id": r.entity_id,
            "message": r.message,
            "payload_json": r.payload_json,
        }
        for r in rows
    ]


@router.get("/logs")
def tail_logs(lines: int = Query(default=200, ge=1, le=2000), path: str = Query(default="backend/logs/app.log")):
    p = Path(path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Log file not found")
    text = p.read_text(encoding="utf-8", errors="replace").splitlines()
    return {"path": str(p), "lines": text[-lines:]}


@router.get("/printers")
def list_windows_printers():
    try:
        import win32print  # type: ignore
    except Exception:
        return {"available": False, "printers": [], "error": "pywin32 not available"}

    try:
        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        printers = [p[2] for p in win32print.EnumPrinters(flags)]
        default = None
        try:
            default = win32print.GetDefaultPrinter()
        except Exception:
            default = None
        return {"available": True, "default": default, "printers": printers}
    except Exception as e:
        return {"available": False, "printers": [], "error": str(e)}

