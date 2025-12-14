from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PrintJobType(str, PyEnum):
    KITCHEN = "KITCHEN"
    CUSTOMER = "CUSTOMER"


class PrintJobStatus(str, PyEnum):
    PENDING = "PENDING"
    PRINTING = "PRINTING"
    PRINTED = "PRINTED"
    FAILED = "FAILED"


class PrintJob(Base):
    __tablename__ = "print_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)

    job_type: Mapped[PrintJobType] = mapped_column(Enum(PrintJobType, name="print_job_type"), nullable=False)
    printer_name: Mapped[str] = mapped_column(String(200), nullable=False)

    payload_raw: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    status: Mapped[PrintJobStatus] = mapped_column(Enum(PrintJobStatus, name="print_job_status"), default=PrintJobStatus.PENDING, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    printed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    order = relationship("Order", back_populates="print_jobs")
