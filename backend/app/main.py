from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import logging
import time

from fastapi import Request

from app.api.routes.catalog import router as catalog_router
from app.api.routes.health import router as health_router
from app.api.routes.orders import router as orders_router
from app.api.routes.print import router as print_router
from app.api.routes.print_jobs import router as print_jobs_router
from app.api.routes.qz import router as qz_router
from app.api.routes.reports import router as reports_router
from app.api.routes.settings import router as settings_router
from app.api.routes.tables import router as tables_router
from app.api.routes.admin_debug import router as admin_debug_router
from app.core.logging import setup_logging
from app.core.config import settings
from app.db.init_db import create_all, seed_if_empty

app = FastAPI(title="POS Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tables_router)
app.include_router(health_router)
app.include_router(catalog_router)
app.include_router(orders_router)
app.include_router(reports_router)
app.include_router(qz_router)
app.include_router(print_router)
app.include_router(settings_router)
app.include_router(print_jobs_router)
app.include_router(admin_debug_router)


@app.on_event("startup")
def _startup():
    setup_logging()
    create_all()
    seed_if_empty()

    if settings.print_worker_in_app:
        from threading import Thread

        from app.workers.print_worker import run_forever

        t = Thread(target=run_forever, kwargs={"poll_interval_s": 0.75}, daemon=True)
        t.start()


dist_dir = Path(__file__).resolve().parents[2] / "dist"
if dist_dir.exists():
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="frontend")


logger = logging.getLogger("http")


@app.middleware("http")
async def _log_requests(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
        return response
    finally:
        elapsed_ms = int((time.time() - start) * 1000)
        logger.info("%s %s %s %sms", request.method, request.url.path, getattr(response, "status_code", "-"), elapsed_ms)
