from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.timezone import now_local
from app.models import (
    Category,
    Order,
    OrderItem,
    OrderStatus,
    Payment,
    PaymentMethod,
    PaymentStatus,
    Product,
    Table,
)
from app.models.print_job import PrintJob, PrintJobStatus, PrintJobType
from app.services.printing_service import build_receipt_bytes
from app.services.settings_service import get_printer_settings


class OrderError(ValueError):
    pass


def create_order_and_queue_prints(
    db: Session,
    *,
    table_id: int,
    payment_status: str,
    items_in: list[dict],
) -> tuple[Order, list[PrintJob]]:
    """Creates order/items and queues 2 print jobs in ONE transaction."""

    # Table: table_id==0 means takeaway/tezgah
    table: Table | None = None
    if table_id != 0:
        table = db.get(Table, table_id)
        if not table or not table.is_active:
            raise OrderError(f"Table not found: {table_id}")

    if not items_in:
        raise OrderError("No items")

    # Collect product ids
    product_ids = {int(x["product_id"]) for x in items_in}
    products = list(db.scalars(select(Product).where(Product.id.in_(product_ids), Product.is_active == True)))
    by_id = {p.id: p for p in products}
    if len(by_id) != len(product_ids):
        missing = sorted(product_ids - set(by_id.keys()))
        raise OrderError(f"Unknown/inactive product(s): {missing}")

    # Preload categories for snapshot names
    cat_ids = {p.category_id for p in products}
    cats = list(db.scalars(select(Category).where(Category.id.in_(cat_ids))))
    cat_name = {c.id: c.name for c in cats}

    created = now_local()

    order = Order(
        table=table,
        status=OrderStatus.SENT if payment_status == "PENDING" else OrderStatus.PAID,
        payment_status=PaymentStatus.PENDING if payment_status == "PENDING" else PaymentStatus.PAID,
        created_at=created,
        paid_at=created if payment_status == "PAID" else None,
        subtotal=0,
        total=0,
    )

    db.add(order)
    db.flush()  # order.id

    subtotal = 0
    order_items: list[OrderItem] = []
    for it in items_in:
        pid = int(it["product_id"])
        qty = int(it["quantity"])
        if qty <= 0:
            raise OrderError("Quantity must be >=1")

        p = by_id[pid]
        unit_price = int(p.price)  # server-authoritative
        line_total = unit_price * qty

        subtotal += line_total
        order_items.append(
            OrderItem(
                order_id=order.id,
                product_id=p.id,
                name_snapshot=p.name,
                unit_price_snapshot=unit_price,
                qty=qty,
                line_total=line_total,
                category_name_snapshot=cat_name.get(p.category_id),
            )
        )

    order.subtotal = subtotal
    order.total = subtotal

    db.add_all(order_items)

    # Payment record if PAID (cash MVP)
    if payment_status == "PAID":
        db.add(
            Payment(
                order_id=order.id,
                method=PaymentMethod.CASH,
                amount_received=order.total,
                change_given=0,
                paid_at=created,
                note=None,
            )
        )

    # Load order with relations for receipt
    db.flush()
    db.refresh(order)
    order = db.scalar(
        select(Order)
        .options(joinedload(Order.table), joinedload(Order.items))
        .where(Order.id == order.id)
    )
    assert order is not None

    kitchen_printer, customer_printer = get_printer_settings(db)

    jobs: list[PrintJob] = []
    for job_type, printer in [
        (PrintJobType.KITCHEN, kitchen_printer),
        (PrintJobType.CUSTOMER, customer_printer),
    ]:
        payload = build_receipt_bytes(order=order, job_type=job_type)
        jobs.append(
            PrintJob(
                order_id=order.id,
                job_type=job_type,
                printer_name=printer,
                payload_raw=payload,
                status=PrintJobStatus.PENDING,
                attempts=0,
                last_error=None,
                created_at=created,
                printed_at=None,
            )
        )

    db.add_all(jobs)
    db.commit()

    # refresh ids
    for j in jobs:
        db.refresh(j)

    return order, jobs
