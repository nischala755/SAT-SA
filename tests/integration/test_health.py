import importlib

import pytest
from fastapi.testclient import TestClient
from sat_sa.config.settings import Settings
from tests.integration.test_repository import dataset


def factory():
    try:
        return importlib.import_module("sat_sa_api.main").create_app
    except ModuleNotFoundError:
        pytest.fail("FastAPI application has not been implemented")


def test_lifespan_and_actual_storage_status(tmp_path):
    app = factory()(Settings(storage_root=tmp_path))
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["registered_datasets"] == 0
        assert response.json()["storage_ready"] is True
        app.state.repository.register_dataset(dataset())
        assert client.get("/api/v1/health").json()["registered_datasets"] == 1
        assert client.get("/openapi.json").status_code == 200
        assert client.get("/docs").status_code == 404  # No remote Swagger CDN.
        assert client.get("/api/v1/ground-truth").status_code == 404
        assert client.get("/api/v1/signals").status_code == 404
        app.state.repository.close()
        failed = client.get("/api/v1/health")
        assert failed.status_code == 503
        assert failed.json()["storage_ready"] is False
        assert failed.json()["registered_datasets"] is None


def test_startup_storage_failure_is_explicit(tmp_path):
    path = tmp_path / "file"
    path.write_text("not a directory")
    with pytest.raises(OSError):
        with TestClient(factory()(Settings(storage_root=path))):
            pass


def test_application_restart_keeps_dataset(tmp_path):
    make = factory()
    with TestClient(make(Settings(storage_root=tmp_path))) as client:
        client.app.state.repository.register_dataset(dataset())
    with TestClient(make(Settings(storage_root=tmp_path))) as client:
        assert client.get("/api/v1/health").json()["registered_datasets"] == 1
