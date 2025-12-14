from __future__ import annotations

import time

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.timezone import now_local
from app.db.session import SessionLocal, init_db
from app.models.print_job import PrintJob
from app.services.printing_service import PrintingService
from app.services.settings_service import SettingsService


_db_initialized = False


def _claim_next_job(db: Session) -> PrintJob | None:
    job_id = db.execute(
        select(PrintJob.id)
        .where(PrintJob.status == "PENDING", PrintJob.attempts < 3)
        .order_by(PrintJob.created_at.asc(), PrintJob.id.asc())
        .limit(1)
    ).scalar_one_or_none()
    if not job_id:
        return None

    updated = db.execute(
        update(PrintJob)
        .where(PrintJob.id == job_id, PrintJob.status == "PENDING")
        .values(status="PRINTING", attempts=PrintJob.attempts + 1)
    ).rowcount
    db.commit()
    if not updated:
        return None
    return db.get(PrintJob, job_id)


def process_next_job(db: Session, printer: PrintingService) -> bool:
    global _db_initialized
    if not _db_initialized:
        init_db()
        _db_initialized = True

    s = SettingsService().get_app_settings(db)
    if (s.print_strategy or "").lower() == "qz":
        return False

    job = _claim_next_job(db)
    if not job:
        return False

    try:
        printer.send_raw(job.printer_name, job.payload_raw, mode=s.print_mode, output_dir=s.print_output_dir)
        job.status = "PRINTED"
        job.printed_at = now_local()
        job.last_error = None
    except Exception as e:
        job.last_error = str(e)
        job.status = "FAILED" if job.attempts >= 3 else "PENDING"
    finally:
        db.add(job)
        db.commit()
    return True


def run_forever(poll_interval_s: float = 0.75) -> None:
    init_db()
    printer = PrintingService()
    while True:
        with SessionLocal() as db:
            did = process_next_job(db, printer)
        if not did:
            time.sleep(poll_interval_s)


if __name__ == "__main__":
    run_forever()
