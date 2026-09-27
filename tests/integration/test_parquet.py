import importlib
import hashlib

import pytest
import pyarrow.parquet as pq
from tests.fixtures.evidence import small_records


def module():
    try:
        return importlib.import_module("sat_sa.repositories.parquet_evidence")
    except ModuleNotFoundError:
        pytest.fail("Parquet evidence repository has not been implemented")


def test_typed_roundtrip_manifest_and_immutability(tmp_path):
    repo = module().ParquetEvidenceRepository(tmp_path)
    manifest = repo.write_dataset(small_records(), tmp_path / "D1", seed=1)
    assert len(manifest.artifacts) == 6
    for artifact in manifest.artifacts:
        assert hashlib.sha256((tmp_path / "D1" / artifact.filename).read_bytes()).hexdigest() == artifact.sha256
    alert = repo.read_records("D1", "alerts", "E1", limit=10)[0]
    assert alert == small_records()["alerts"][0]
    assert alert.escalation_timestamp is None
    assert alert.timestamp.tzinfo is not None
    schema = pq.read_schema(tmp_path / "D1/alerts.parquet")
    assert str(schema.field("timestamp").type) == "timestamp[us, tz=UTC]"
    assert str(schema.field("escalation_required").type) == "bool"
    with pytest.raises(FileExistsError):
        repo.write_dataset(small_records(), tmp_path / "D1", seed=2)
    assert repo.read_records("D1", "alerts", "OTHER", limit=10) == []


@pytest.mark.parametrize("kind", ["ground_truth", "../ground_truth/labels", "alerts.parquet"])
def test_only_whitelisted_evidence_tables_are_readable(tmp_path, kind):
    repo = module().ParquetEvidenceRepository(tmp_path)
    with pytest.raises(ValueError):
        repo.read_records("D1", kind, "E1", limit=10)


def test_paths_and_limits_are_bounded(tmp_path):
    repo = module().ParquetEvidenceRepository(tmp_path)
    with pytest.raises(ValueError):
        repo.read_records("../labels", "alerts", "E1", limit=10)
    with pytest.raises(ValueError):
        repo.read_records("D1", "alerts", "E1", limit=1001)
    with pytest.raises(ValueError):
        repo.write_dataset(small_records(), tmp_path.parent / "outside", seed=1)


def test_cross_entity_reference_rejected_and_no_partial_publication(tmp_path):
    repo = module().ParquetEvidenceRepository(tmp_path)
    records = small_records()
    records["cses"].append(records["cses"][0].model_copy(update={"cse_id": "E2"}))
    records["alerts"] = [records["alerts"][0].model_copy(update={"cse_id": "E2"})]
    with pytest.raises(ValueError, match="asset reference"):
        repo.write_dataset(records, tmp_path / "D1", seed=1)
    assert not (tmp_path / "D1").exists()
