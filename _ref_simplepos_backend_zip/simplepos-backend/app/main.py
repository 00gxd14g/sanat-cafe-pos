from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    catalog_router,
    health_router,
    orders_router,
    print_jobs_router,
    reports_router,
    settings_router,
    tables_router,
)
from app.core.config import settings
from app.db.init_db import create_all, seed_if_empty
from app.workers.print_worker import worker


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)

    origins = [o.strip() for o in settings.CORS_ALLOW_ORIGINS.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(health_router)
    app.include_router(catalog_router)
    app.include_router(tables_router)
    app.include_router(orders_router)
    app.include_router(reports_router)
    app.include_router(settings_router)
    app.include_router(print_jobs_router)

    @app.on_event("startup")
    def _startup() -> None:
        create_all()
        seed_if_empty()
        if settings.RUN_PRINT_WORKER:
            worker.start()

    @app.on_event("shutdown")
    def _shutdown() -> None:
        if settings.RUN_PRINT_WORKER:
            worker.stop()

    return app


app = create_app()
