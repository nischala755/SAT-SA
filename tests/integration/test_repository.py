import importlib
import json
import subprocess
import sys
from datetime import datetime, timezone

import pytest
from sat_sa_contracts.models import AuditEvent, DatasetVersion


def module():
    try:
        return importlib.import_module("sat_sa.repositories.duckdb_metadata")
    except ModuleNotFoundError:
        pytest.fail("DuckDB metadata repository has not been implemented")


def dataset():
    return DatasetVersion(dataset_id="D1", dataset_hash="a" * 64, schema_version="1", created_at="2026-01-01T00:00:00Z", assessment_period={"start": "2025-01-01T00:00:00Z", "end": "2026-01-01T00:00:00Z"}, artifacts=())


def event(event_id="audit1"):
    return AuditEvent(event_id=event_id, timestamp=datetime.now(timezone.utc), actor="O'Brien", role="administrator", action="local test", object_id="D1", details={"text": "'); DROP TABLE datasets; --"})


def test_reopen_and_process_restart_preserve_data(tmp_path):
    cls = module().DuckDBMetadataRepository
    db = tmp_path / "metadata.duckdb"
    with cls(db) as repo:
        repo.initialize()
        assert repo.status() == {"storage_ready": True, "registered_datasets": 0}
        repo.register_dataset(dataset())
        repo.append_audit(event())
        assert [row.action for row in repo.list_audit()] == ["dataset_registered", "local test"]
    with cls(db) as repo:
        repo.initialize()
        assert repo.get_dataset("D1") == dataset()
        assert repo.list_audit()[1].actor == "O'Brien"
        assert repo.status()["registered_datasets"] == 1
    code = "from sat_sa.repositories.duckdb_metadata import DuckDBMetadataRepository as R; import sys; r=R(sys.argv[1]); r.initialize(); print(r.status()['registered_datasets']); print(len(r.list_audit())); r.close()"
    result = subprocess.run([sys.executable, "-c", code, str(db)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ["1", "2"]


def test_duplicate_registration_never_overwrites(tmp_path):
    mod = module()
    with mod.DuckDBMetadataRepository(tmp_path / "db") as repo:
        repo.initialize()
        repo.register_dataset(dataset())
        for duplicate in [dataset(), dataset().model_copy(update={"dataset_hash": "b" * 64})]:
            with pytest.raises(mod.DuplicateDatasetError):
                repo.register_dataset(duplicate)
        assert repo.get_dataset("D1").dataset_hash == "a" * 64
        assert len(repo.list_audit()) == 1


def test_registration_and_audit_are_atomic(tmp_path):
    cls = module().DuckDBMetadataRepository
    with cls(tmp_path / "db") as repo:
        repo.initialize()
        repo.append_audit(event("register:D1"))
        with pytest.raises(Exception):
            repo.register_dataset(dataset())
        assert repo.get_dataset("D1") is None
        assert len(repo.list_audit()) == 1


def test_storage_failure_is_not_healthy(tmp_path):
    cls = module().DuckDBMetadataRepository
    invalid = tmp_path / "not-a-directory"
    invalid.write_text("file")
    with pytest.raises(OSError):
        cls(invalid / "db").initialize()


def test_maximum_length_dataset_identifier_can_be_registered(tmp_path):
    cls = module().DuckDBMetadataRepository
    value = DatasetVersion.model_validate(dataset().model_dump() | {"dataset_id": "D" * 160})
    with cls(tmp_path / "db") as repo:
        repo.initialize()
        repo.register_dataset(value)
        assert repo.get_dataset(value.dataset_id) == value
        assert len(repo.list_audit()[0].event_id) <= 160
