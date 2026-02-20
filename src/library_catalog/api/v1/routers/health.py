"""
Роутер для health check.
"""

from fastapi import APIRouter
from sqlalchemy import text

from src.library_catalog.api.v1.schemas.common import HealthCheckResponse
from src.library_catalog.api.dependencies import DbSessionDep

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "/",
    response_model=HealthCheckResponse,
    summary="Health Check",
)
async def health_check(db: DbSessionDep):
    """Проверить состояние сервиса и подключение к БД."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return HealthCheckResponse(status="healthy", database=db_status)
