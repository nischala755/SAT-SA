"""Phase 1 status API. No evidence ingestion or analytical endpoints exist."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sat_sa.repositories.duckdb_metadata import DuckDBMetadataRepository
from .settings import Settings, load_settings
from .schemas import HealthStatus

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        with DuckDBMetadataRepository(settings.storage_root / "metadata.duckdb") as repository:
            repository.initialize()  # Startup fails explicitly on unusable storage.
            app.state.repository = repository
            yield

    app = FastAPI(title="SAT-SA — Supervisory Analytics Tool for SOC Assessment", version="0.1.0", lifespan=lifespan, docs_url=None, redoc_url=None)

    @app.get("/api/v1/health", response_model=HealthStatus, responses={503: {"model": HealthStatus}})
    def health():
        try:
            status = app.state.repository.status()
            return HealthStatus(status="ok", demo_mode=settings.demo_mode, message="Local metadata storage ready", **status)
        except Exception:
            logger.exception("Metadata health check failed")
            result = HealthStatus(status="unavailable", demo_mode=settings.demo_mode, storage_ready=False, registered_datasets=None, message="Metadata storage unavailable; inspect local service logs")
            return JSONResponse(status_code=503, content=result.model_dump(mode="json"))

    return app
