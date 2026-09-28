"""SAT-SA API factory, storage health and persisted workflow lifecycle."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sat_sa.repositories.workflow import WorkflowRepository
from .workflow import Workflow
from .routes import router
from .settings import Settings, load_settings
from .schemas import HealthStatus

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        with WorkflowRepository(settings.storage_root / "metadata.duckdb") as repository:
            repository.initialize()  # Startup fails explicitly on unusable storage.
            app.state.repository = repository
            repository.recover_jobs()
            app.state.workflow = Workflow(repository,settings)
            if settings.demo_mode and repository.get_dataset('demo') and not repository.runs():
                app.state.workflow.submit('analytics','demo',{'actor':'demo-bootstrap','role':'administrator'})
            try:
                yield
            finally:
                app.state.workflow.close()

    app = FastAPI(title="SAT-SA — Supervisory Analytics Tool for SOC Assessment", version="0.1.0", lifespan=lifespan, docs_url=None, redoc_url=None)
    app.include_router(router(settings))

    @app.middleware('http')
    async def payload_limit(request,call_next):
        if request.method in ('POST','PUT','PATCH'):
            size=0; chunks=[]
            async for chunk in request.stream():
                size+=len(chunk)
                if size>24000000: return JSONResponse(status_code=413,content={'detail':'Request exceeds 24 MB limit'})
                chunks.append(chunk)
            request._body=b''.join(chunks)
        response=await call_next(request)
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Cache-Control']='no-store'
        return response

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
