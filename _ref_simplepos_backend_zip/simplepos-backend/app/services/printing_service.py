from __future__ import annotations

import os
from pathlib import Path

from app.core.config import settings
from app.core.timezone import now_local
from app.models import Order
from app.models.print_job import PrintJobType

try:
    import win32print  # type: ignore
except Exception:  # pragma: no cover
    win32print = None  # type: ignore


CUT_PARTIAL = b"\x1dV\x41\x03"  # GS V A n (partial cut)


def _line(width: int, ch: str = "-") -> str:
    return ch * width


def _truncate(s: str, width: int) -> str:
    s = s.strip()
    if len(s) <= width:
        return s
    return s[: max(0, width - 1)] + "…"


def _fmt_money_try(amount: int) -> str:
    return f"{amount}₺"


def build_receipt_bytes(
    *,
    order: Order,
    job_type: PrintJobType,
    line_width: int | None = None,
    encoding: str | None = None,
) -> bytes:
    """Generate printable bytes for 58mm ESC/POS-like printers."""
    lw = line_width or settings.RECEIPT_LINE_WIDTH
    enc = encoding or settings.RECEIPT_ENCODING

    ts = order.created_at or now_local()
    dt = ts.strftime("%Y-%m-%d %H:%M")

    header = "MUTFAK" if job_type == PrintJobType.KITCHEN else "MÜŞTERİ"
    table_str = f"Masa: {order.table.name}" if order.table else "Tezgah / Paket"

    lines: list[str] = [
        _truncate(settings.APP_NAME, lw),
        _truncate(header, lw),
        _truncate(dt, lw),
        _truncate(table_str, lw),
        _line(lw),
    ]

    for it in order.items:
        qty = it.qty
        name = it.name_snapshot
        if job_type == PrintJobType.KITCHEN:
            lines.append(_truncate(f"{qty}x {name}", lw))
        else:
            left = _truncate(f"{qty}x {name}", lw - 8)
            right = _fmt_money_try(it.line_total)
            pad = max(1, lw - len(left) - len(right))
            lines.append(left + " " * pad + right)

    lines.append(_line(lw))

    if job_type == PrintJobType.CUSTOMER:
        total = _fmt_money_try(order.total)
        label = "TOPLAM"
        pad = max(1, lw - len(label) - len(total))
        lines.append(label + " " * pad + total)
        lines.append(_line(lw))
        lines.append(_truncate("Teşekkürler!", lw))

    text = "\n".join(lines) + "\n\n"
    try:
        payload = text.encode(enc, errors="replace")
    except Exception:
        payload = text.encode("utf-8", errors="replace")

    return payload + CUT_PARTIAL


def _spool_fallback(printer_name: str, payload: bytes) -> None:
    spool_dir = Path("./print_spool")
    spool_dir.mkdir(parents=True, exist_ok=True)
    fname = spool_dir / f"spool_{printer_name}_{now_local().strftime('%Y%m%d_%H%M%S_%f')}.bin"
    fname.write_bytes(payload)


def send_raw_to_printer(printer_name: str, payload: bytes) -> None:
    """Send RAW bytes to a printer.

    - Windows + pywin32: sends to Windows spooler (RAW).
    - Otherwise: writes a spool file under ./print_spool (so the app still runs).
    """
    if win32print is None or os.name != "nt":  # pragma: no cover
        _spool_fallback(printer_name, payload)
        return

    h = win32print.OpenPrinter(printer_name)
    try:
        job_id = win32print.StartDocPrinter(h, 1, ("POS Receipt", None, "RAW"))
        try:
            win32print.StartPagePrinter(h)
            win32print.WritePrinter(h, payload)
            win32print.EndPagePrinter(h)
        finally:
            win32print.EndDocPrinter(h)
    finally:
        win32print.ClosePrinter(h)
