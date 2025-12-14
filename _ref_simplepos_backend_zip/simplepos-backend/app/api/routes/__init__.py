from .health import router as health_router
from .catalog import router as catalog_router
from .tables import router as tables_router
from .orders import router as orders_router
from .reports import router as reports_router
from .settings import router as settings_router
from .print_jobs import router as print_jobs_router

__all__ = [
    "health_router",
    "catalog_router",
    "tables_router",
    "orders_router",
    "reports_router",
    "settings_router",
    "print_jobs_router",
]
