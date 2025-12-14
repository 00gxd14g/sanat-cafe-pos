from __future__ import annotations

from datetime import datetime

from dateutil.tz import gettz

from app.core.config import settings


def now_local() -> datetime:
    tz = gettz(settings.TZ)
    return datetime.now(tz)
