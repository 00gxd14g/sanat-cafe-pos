from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False, index=True)
    method: Mapped[str] = mapped_column(String(20), nullable=False, default="CASH")
    amount_received: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    change_given: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

