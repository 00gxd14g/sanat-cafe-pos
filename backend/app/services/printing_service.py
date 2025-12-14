from __future__ import annotations

import os
from pathlib import Path

from app.core.config import settings


class PrintingService:
    def send_raw(self, printer_name: str, payload: bytes, *, mode: str | None = None, output_dir: str | None = None) -> None:
        mode = (mode or settings.print_mode or "file").lower()
        if mode == "noop":
            return
        if mode == "file":
            base = Path(output_dir or settings.print_output_dir)
            base.mkdir(parents=True, exist_ok=True)
            filename = base / f"print_{os.getpid()}_{id(payload)}.bin"
            filename.write_bytes(payload)
            return
        if mode == "spooler":
            try:
                self._send_raw_spooler(printer_name, payload)
            except Exception:
                self._spool_fallback(printer_name or "default", payload)
            return
        raise ValueError(f"Unknown PRINT_MODE: {settings.print_mode}")

    def _spool_fallback(self, printer_name: str, payload: bytes) -> None:
        spool_dir = Path("./print_spool")
        spool_dir.mkdir(parents=True, exist_ok=True)
        filename = spool_dir / f"spool_{printer_name}_{os.getpid()}_{id(payload)}.bin"
        filename.write_bytes(payload)

    def _send_raw_spooler(self, printer_name: str, payload: bytes) -> None:
        try:
            import win32print  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError("pywin32 is required for PRINT_MODE=spooler") from e

        target = printer_name or None
        if not target:
            target = win32print.GetDefaultPrinter()

        handle = win32print.OpenPrinter(target)
        try:
            job = win32print.StartDocPrinter(handle, 1, ("POS Print Job", None, "RAW"))
            try:
                win32print.StartPagePrinter(handle)
                win32print.WritePrinter(handle, payload)
                win32print.EndPagePrinter(handle)
            finally:
                win32print.EndDocPrinter(handle)
        finally:
            win32print.ClosePrinter(handle)


def send_raw_to_printer(printer_name: str, payload: bytes) -> None:
    PrintingService().send_raw(printer_name, payload, mode="spooler")
