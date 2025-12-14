from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
from zoneinfo import ZoneInfoNotFoundError

from app.core.config import settings


def tzinfo() -> ZoneInfo:
    try:
        return ZoneInfo(settings.tz)
    except ZoneInfoNotFoundError:
        local = datetime.now().astimezone().tzinfo
        return local if isinstance(local, ZoneInfo) else ZoneInfo("UTC")


def now_local() -> datetime:
    return datetime.now(tzinfo())
