from __future__ import annotations

import logging
from pathlib import Path


def setup_logging(log_path: str = "backend/logs/app.log") -> None:
    root = logging.getLogger()
    if getattr(root, "_pos_logging_configured", False):
        return

    root.setLevel(logging.INFO)

    log_file = Path(log_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)

    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(fmt)

    root.addHandler(fh)
    root.addHandler(sh)
    root._pos_logging_configured = True  # type: ignore[attr-defined]

