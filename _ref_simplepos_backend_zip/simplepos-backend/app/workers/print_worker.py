from __future__ import annotations

import threading
import time
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.timezone import now_local
from app.db.session import SessionLocal
from app.models import Order
from app.models.print_job import PrintJob, PrintJobStatus
from app.services.printing_service import send_raw_to_printer


class PrintWorker:
    def __init__(self) -> None:
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run_loop, name="print-worker", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _run_loop(self) -> None:
        poll = max(0.2, float(settings.PRINT_POLL_SECONDS))

        while not self._stop.is_set():
            try:
                self._tick()
            except Exception:
                # Keep worker alive; errors get recorded per job when possible.
                pass
            time.sleep(poll)

    def _tick(self) -> None:
        db: Session = SessionLocal()
        try:
            job = db.scalar(
                select(PrintJob)
                .where(
                    PrintJob.status == PrintJobStatus.PENDING,
                    PrintJob.attempts < settings.PRINT_MAX_ATTEMPTS,
                )
                .order_by(PrintJob.id.asc())
                .limit(1)
            )
            if not job:
                return

            # Mark as printing
            job.status = PrintJobStatus.PRINTING
            job.attempts = int(job.attempts) + 1
            db.commit()
            db.refresh(job)

            # Print
            try:
                send_raw_to_printer(job.printer_name, job.payload_raw)
                job.status = PrintJobStatus.PRINTED
                job.printed_at = now_local()
                job.last_error = None
            except Exception as e:
                job.status = PrintJobStatus.FAILED
                job.last_error = str(e)

            db.commit()
        finally:
            db.close()


worker = PrintWorker()
