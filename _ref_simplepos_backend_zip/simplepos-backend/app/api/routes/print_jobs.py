from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.print_job import PrintJob, PrintJobStatus
from app.schemas.printing import PrintJobDebugOut

router = APIRouter(prefix="/api", tags=["printing"])


@router.get("/print-jobs", response_model=list[PrintJobDebugOut])
def list_print_jobs(db: Session = Depends(get_db)):
    jobs = list(db.scalars(select(PrintJob).order_by(PrintJob.id.desc()).limit(200)))
    return [
        PrintJobDebugOut(
            id=j.id,
            order_id=j.order_id,
            job_type=j.job_type.value,
            printer_name=j.printer_name,
            status=j.status.value,
            attempts=j.attempts,
            last_error=j.last_error,
        )
        for j in jobs
    ]


@router.post("/print-jobs/{job_id}/retry", response_model=PrintJobDebugOut)
def retry_print_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(PrintJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Print job not found")

    job.status = PrintJobStatus.PENDING
    job.last_error = None
    db.commit()
    db.refresh(job)

    return PrintJobDebugOut(
        id=job.id,
        order_id=job.order_id,
        job_type=job.job_type.value,
        printer_name=job.printer_name,
        status=job.status.value,
        attempts=job.attempts,
        last_error=job.last_error,
    )
