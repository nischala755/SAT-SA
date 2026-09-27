import importlib
import pytest
from sat_sa.config.settings import Settings
from sat_sa.repositories.duckdb_metadata import DuckDBMetadataRepository


def bootstrap():
    try:
        return importlib.import_module("sat_sa.synthetic.bootstrap").ensure_demo
    except ModuleNotFoundError:
        pytest.fail("Idempotent demo bootstrap has not been implemented")


def test_bootstrap_is_idempotent_and_rejects_changed_seed(tmp_path):
    ensure = bootstrap()
    settings = Settings(storage_root=tmp_path)
    first = ensure(settings)
    assert ensure(settings) == first
    with DuckDBMetadataRepository(tmp_path / "metadata.duckdb") as repo:
        repo.initialize()
        assert repo.status()["registered_datasets"] == 1
        assert len(repo.list_audit()) == 1
    with pytest.raises(ValueError, match="seed"):
        ensure(Settings(storage_root=tmp_path, demo_seed=1))


def test_bootstrap_detects_corrupt_artifact(tmp_path):
    ensure = bootstrap()
    settings = Settings(storage_root=tmp_path)
    ensure(settings)
    with (tmp_path / "evidence/demo/alerts.parquet").open("ab") as file:
        file.write(b"corruption")
    with pytest.raises(ValueError, match="integrity"):
        ensure(settings)
