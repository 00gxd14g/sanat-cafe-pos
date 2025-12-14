from __future__ import annotations

from datetime import date, datetime, time, timedelta

from dateutil.tz import gettz
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Order, OrderItem, PaymentStatus


def _day_range(d: date) -> tuple[datetime, datetime]:
    tz = gettz(settings.TZ)
    start = datetime.combine(d, time.min).replace(tzinfo=tz)
    end = start + timedelta(days=1)
    return start, end


def get_daily_stats(db: Session, d: date) -> dict:
    start, end = _day_range(d)

    total_revenue = db.scalar(
        select(func.coalesce(func.sum(Order.total), 0)).where(
            Order.payment_status == PaymentStatus.PAID,
            Order.paid_at >= start,
            Order.paid_at < end,
        )
    ) or 0

    total_orders = db.scalar(
        select(func.count(Order.id)).where(
            Order.created_at >= start,
            Order.created_at < end,
        )
    ) or 0

    total_items = db.scalar(
        select(func.coalesce(func.sum(OrderItem.qty), 0))
        .join(Order, OrderItem.order_id == Order.id)
        .where(Order.created_at >= start, Order.created_at < end)
    ) or 0

    return {
        "total_revenue": int(total_revenue),
        "total_orders": int(total_orders),
        "total_items": int(total_items),
    }


def get_daily_sales_data(db: Session, d: date) -> list[dict]:
    start, end = _day_range(d)

    rows = db.execute(
        select(
            func.coalesce(OrderItem.category_name_snapshot, "Diğer").label("name"),
            func.coalesce(func.sum(OrderItem.line_total), 0).label("value"),
        )
        .join(Order, OrderItem.order_id == Order.id)
        .where(
            Order.payment_status == PaymentStatus.PAID,
            Order.paid_at >= start,
            Order.paid_at < end,
        )
        .group_by(func.coalesce(OrderItem.category_name_snapshot, "Diğer"))
        .order_by(func.sum(OrderItem.line_total).desc())
    ).all()

    return [{"name": str(r.name), "value": int(r.value)} for r in rows]
