from __future__ import annotations

from enum import Enum


class TableStatus(str, Enum):
    EMPTY = "empty"
    OCCUPIED = "occupied"
