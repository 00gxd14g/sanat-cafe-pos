from __future__ import annotations

from datetime import date, datetime, time, timedelta

from dateutil.tz import gettz
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.category import Category
from app.models.order import Order, OrderItem


def _day_range(d: date) -> tuple[datetime, datetime]:
    tz = gettz(settings.tz)
    start = datetime.combine(d, time.min).replace(tzinfo=tz)
    end = start + timedelta(days=1)
    return start, end


def get_daily_stats(db: Session, d: date) -> dict:
    start, end = _day_range(d)

    total_revenue = (
        db.execute(
            select(func.coalesce(func.sum(Order.total), 0)).where(
                Order.payment_status == "PAID",
                Order.paid_at >= start,
                Order.paid_at < end,
            )
        ).scalar_one()
        or 0
    )

    total_orders = (
        db.execute(select(func.count(Order.id)).where(Order.created_at >= start, Order.created_at < end)).scalar_one() or 0
    )

    total_items = (
        db.execute(
            select(func.coalesce(func.sum(OrderItem.qty), 0))
            .join(Order, OrderItem.order_id == Order.id)
            .where(Order.created_at >= start, Order.created_at < end)
        ).scalar_one()
        or 0
    )

    return {
        "total_revenue": float(total_revenue),
        "total_orders": int(total_orders),
        "total_items": int(total_items),
    }


def get_daily_sales_data(db: Session, d: date) -> list[dict]:
    start, end = _day_range(d)

    rows = db.execute(
        select(
            func.coalesce(Category.name, "Di?er").label("name"),
            func.coalesce(func.sum(OrderItem.line_total), 0).label("value"),
        )
        .select_from(OrderItem)
        .join(Order, OrderItem.order_id == Order.id)
        .outerjoin(Category, Category.id == OrderItem.category_id_snapshot)
        .where(
            Order.payment_status == "PAID",
            Order.paid_at >= start,
            Order.paid_at < end,
        )
        .group_by(func.coalesce(Category.name, "Di?er"))
        .order_by(func.sum(OrderItem.line_total).desc())
    ).all()

    return [{"name": str(r.name), "value": float(r.value)} for r in rows]
