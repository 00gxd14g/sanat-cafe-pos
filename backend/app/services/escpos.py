from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


def _hr_text() -> str:
    return "-" * 32


def _cut_bytes() -> bytes:
    return b"\n\n\x1dV\x41\x00"


@dataclass(frozen=True)
class PrintLineItem:
    name: str
    qty: int
    unit_price: float
    line_total: float


def render_receipt_commands(
    *,
    title: str,
    created_at: datetime,
    table_label: str,
    items: list[PrintLineItem],
    total: float,
    show_prices: bool,
) -> list[str]:
    lines: list[str] = []
    lines.append("\x1b@")  # ESC @ init
    lines.append(f"{title}\n")
    lines.append(f"{created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"{table_label}\n")
    lines.append(f"{_hr_text()}\n")
    for it in items:
        lines.append(f"{it.qty}x {it.name}\n")
        if show_prices:
            lines.append(f"   {it.unit_price:.2f} -> {it.line_total:.2f}\n")
    lines.append(f"{_hr_text()}\n")
    if show_prices:
        lines.append(f"TOPLAM: {total:.2f}\n")
    lines.append("\n\n\n")
    lines.append("\x1dV\x41\x00")  # GS V A 0 cut (optional)
    return lines


def render_receipt_bytes(
    *,
    encoding: str,
    title: str,
    created_at: datetime,
    table_label: str,
    items: list[PrintLineItem],
    total: float,
    show_prices: bool,
) -> bytes:
    parts = render_receipt_commands(
        title=title,
        created_at=created_at,
        table_label=table_label,
        items=items,
        total=total,
        show_prices=show_prices,
    )
    joined = "".join(parts)
    try:
        return joined.encode(encoding, errors="replace")
    except Exception:
        return joined.encode("utf-8", errors="replace")
