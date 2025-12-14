from __future__ import annotations

from datetime import date, datetime, time

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.timezone import now_local
from app.models.category import Category
from app.models.order import Order, OrderItem
from app.models.payment import Payment
from app.models.print_job import PrintJob
from app.models.product import Product
from app.models.table import Table
from app.schemas.orders import OrderCreateIn
from app.services.escpos import PrintLineItem, render_receipt_bytes
from app.services.settings_service import SettingsService


class OrderService:
    def create_order(self, db: Session, payload: OrderCreateIn) -> tuple[Order, list[PrintJob]]:
        if payload.payment_status not in {"PAID", "PENDING"}:
            raise ValueError("payment_status must be PAID or PENDING")

        table_id: int | None
        if payload.table_id == 0:
            table_id = None
        elif payload.table_id > 0:
            table = db.get(Table, payload.table_id)
            if not table or not table.is_active:
                raise ValueError("table_id is invalid")
            table_id = table.id
        else:
            raise ValueError("table_id is invalid")

        product_ids = [i.product_id for i in payload.items]
        products = list(
            db.execute(
                select(Product).where(Product.id.in_(product_ids), Product.is_active.is_(True), Product.price.is_not(None), Product.price > 0)
            ).scalars()
        )
        products_by_id = {p.id: p for p in products}
        if len(products_by_id) != len(set(product_ids)):
            raise ValueError("one or more products are invalid or inactive")

        created_at = now_local()
        app_settings = SettingsService().get_app_settings(db)
        order = Order(
            table_id=table_id,
            status="PAID" if payload.payment_status == "PAID" else "SENT",
            subtotal=0,
            total=0,
            payment_status=payload.payment_status,
            created_at=created_at,
            paid_at=created_at if payload.payment_status == "PAID" else None,
        )
        db.add(order)
        db.flush()

        subtotal = 0.0
        order_items: list[OrderItem] = []
        print_items: list[PrintLineItem] = []
        for item in payload.items:
            product = products_by_id[item.product_id]
            unit_price = float(product.price)
            line_total = unit_price * item.quantity
            subtotal += line_total
            order_items.append(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    name_snapshot=product.name,
                    unit_price_snapshot=unit_price,
                    qty=item.quantity,
                    line_total=line_total,
                    category_id_snapshot=product.category_id,
                )
            )
            print_items.append(
                PrintLineItem(name=product.name, qty=item.quantity, unit_price=unit_price, line_total=line_total)
            )

        order.subtotal = subtotal
        order.total = subtotal
        db.add_all(order_items)

        if payload.payment_status == "PAID":
            db.add(
                Payment(
                    order_id=order.id,
                    method="CASH",
                    amount_received=order.total,
                    change_given=0,
                    paid_at=created_at,
                )
            )

        table_label = f"Masa {payload.table_id}" if table_id is not None else "Paket Servis"
        kitchen_payload = render_receipt_bytes(
            encoding=app_settings.qz_encoding,
            title="MUTFAK",
            created_at=created_at,
            table_label=table_label,
            items=print_items,
            total=float(order.total),
            show_prices=app_settings.kitchen_show_prices,
        )
        customer_payload = render_receipt_bytes(
            encoding=app_settings.qz_encoding,
            title="MUSTERI",
            created_at=created_at,
            table_label=table_label,
            items=print_items,
            total=float(order.total),
            show_prices=app_settings.customer_show_prices,
        )

        initial_job_status = "PENDING" if (app_settings.print_strategy or "").lower() != "qz" else "CLIENT_PENDING"
        jobs = [
            PrintJob(
                order_id=order.id,
                job_type="KITCHEN",
                printer_name=app_settings.printer_kitchen_name,
                payload_raw=kitchen_payload,
                status=initial_job_status,
                attempts=0,
                created_at=created_at,
            ),
            PrintJob(
                order_id=order.id,
                job_type="CUSTOMER",
                printer_name=app_settings.printer_customer_name,
                payload_raw=customer_payload,
                status=initial_job_status,
                attempts=0,
                created_at=created_at,
            ),
        ]
        db.add_all(jobs)

        db.commit()
        for j in jobs:
            db.refresh(j)
        db.refresh(order)
        return order, jobs

    def list_tables_for_dashboard(self, db: Session) -> list[dict]:
        tables = list(db.execute(select(Table).where(Table.is_active.is_(True)).order_by(Table.id.asc())).scalars())
        if not tables:
            return []

        sums = {
            table_id: float(total or 0)
            for table_id, total in db.execute(
                select(Order.table_id, func.sum(Order.total))
                .where(Order.table_id.is_not(None), Order.payment_status == "PENDING")
                .group_by(Order.table_id)
            ).all()
        }

        out: list[dict] = []
        for t in tables:
            total_amount = sums.get(t.id, 0.0)
            if total_amount > 0:
                out.append({"id": t.id, "name": t.name, "status": "occupied", "total_amount": total_amount})
            else:
                out.append({"id": t.id, "name": t.name, "status": "empty"})
        return out

    def daily_window(self, d: date) -> tuple[datetime, datetime]:
        start = datetime.combine(d, time.min)
        end = datetime.combine(d, time.max)
        return start, end

    def daily_stats(self, db: Session, d: date) -> dict:
        start, end = self.daily_window(d)

        total_revenue = float(
            db.execute(
                select(func.coalesce(func.sum(Order.total), 0)).where(
                    Order.payment_status == "PAID", Order.created_at >= start, Order.created_at <= end
                )
            ).scalar_one()
        )
        total_orders = int(
            db.execute(select(func.count(Order.id)).where(Order.created_at >= start, Order.created_at <= end)).scalar_one()
        )
        total_items = int(
            db.execute(
                select(func.coalesce(func.sum(OrderItem.qty), 0))
                .join(Order, OrderItem.order_id == Order.id)
                .where(Order.created_at >= start, Order.created_at <= end)
            ).scalar_one()
        )

        return {"total_revenue": total_revenue, "total_orders": total_orders, "total_items": total_items}

    def daily_sales_by_category(self, db: Session, d: date) -> list[dict]:
        start, end = self.daily_window(d)

        rows = db.execute(
            select(Category.name, func.coalesce(func.sum(OrderItem.line_total), 0))
            .select_from(OrderItem)
            .join(Order, OrderItem.order_id == Order.id)
            .join(Category, Category.id == OrderItem.category_id_snapshot)
            .where(Order.payment_status == "PAID", Order.created_at >= start, Order.created_at <= end)
            .group_by(Category.name)
            .order_by(func.sum(OrderItem.line_total).desc())
        ).all()
        return [{"name": name, "value": float(value)} for name, value in rows]

    def list_orders(self, db: Session, *, payment_status: str | None = None) -> list[dict]:
        stmt = select(Order).order_by(Order.created_at.desc(), Order.id.desc())
        if payment_status:
            stmt = stmt.where(Order.payment_status == payment_status)
        orders = list(db.execute(stmt.limit(200)).scalars())
        if not orders:
            return []

        order_ids = [o.id for o in orders]
        items = list(
            db.execute(select(OrderItem).where(OrderItem.order_id.in_(order_ids)).order_by(OrderItem.order_id.asc(), OrderItem.id.asc())).scalars()
        )
        items_by_order: dict[int, list[OrderItem]] = {}
        for it in items:
            items_by_order.setdefault(int(it.order_id), []).append(it)

        def _iso(dt):
            return dt.isoformat() if dt is not None else None

        out: list[dict] = []
        for o in orders:
            out.append(
                {
                    "id": o.id,
                    "table_id": o.table_id,
                    "status": o.status,
                    "payment_status": o.payment_status,
                    "total": float(o.total),
                    "created_at": _iso(o.created_at),
                    "paid_at": _iso(o.paid_at),
                    "items": [
                        {
                            "product_id": it.product_id,
                            "name": it.name_snapshot,
                            "quantity": int(it.qty),
                            "unit_price": float(it.unit_price_snapshot),
                            "line_total": float(it.line_total),
                        }
                        for it in items_by_order.get(o.id, [])
                    ],
                }
            )
        return out

    def update_order(self, db: Session, order_id: int, *, status: str | None, payment_status: str | None) -> dict:
        order = db.get(Order, order_id)
        if not order:
            raise ValueError("order not found")

        if status is not None:
            order.status = status
        if payment_status is not None:
            if payment_status not in {"PAID", "PENDING"}:
                raise ValueError("payment_status must be PAID or PENDING")
            order.payment_status = payment_status
            if payment_status == "PAID":
                order.status = "PAID"
                order.paid_at = now_local()
            else:
                if order.status == "PAID":
                    order.status = "SENT"
                order.paid_at = None

        db.add(order)
        db.commit()
        db.refresh(order)
        return self.get_order(db, order.id)

    def get_order(self, db: Session, order_id: int) -> dict:
        order = db.get(Order, order_id)
        if not order:
            raise ValueError("order not found")

        items = list(
            db.execute(select(OrderItem).where(OrderItem.order_id == order_id).order_by(OrderItem.id.asc())).scalars()
        )

        return {
            "id": order.id,
            "table_id": order.table_id,
            "status": order.status,
            "payment_status": order.payment_status,
            "total": float(order.total),
            "created_at": order.created_at.isoformat(),
            "paid_at": order.paid_at.isoformat() if order.paid_at else None,
            "items": [
                {
                    "product_id": it.product_id,
                    "name": it.name_snapshot,
                    "quantity": int(it.qty),
                    "unit_price": float(it.unit_price_snapshot),
                    "line_total": float(it.line_total),
                }
                for it in items
            ],
        }
