import hashlib
import importlib
import json

import pyarrow.parquet as pq
import pytest


def generator():
    try:
        return importlib.import_module("sat_sa.synthetic.generator").generate_dataset
    except ModuleNotFoundError:
        pytest.fail("Seeded dataset generator has not been implemented")


def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}


@pytest.fixture(scope="module")
def generated(tmp_path_factory):
    root = tmp_path_factory.mktemp("synthetic")
    make = generator()
    first = make(20260927, root / "a/evidence/demo", root / "a/labels/demo")
    second = make(20260927, root / "b/evidence/demo", root / "b/labels/demo")
    third = make(20260928, root / "c/evidence/demo", root / "c/labels/demo")
    return root, first, second, third


def test_same_seed_identical_artifacts_and_different_seed_changes(generated):
    root, first, second, third = generated
    assert hashes(root / "a") == hashes(root / "b")
    assert first == second
    assert first.dataset_hash != third.dataset_hash
    for path in (root / "a/evidence/demo").glob("*.parquet"):
        assert pq.read_table(path).to_pylist() == pq.read_table(root / "b/evidence/demo" / path.name).to_pylist()


def test_realistic_scale_periods_and_relations(generated):
    root, manifest, *_ = generated
    rows = {p.stem: pq.read_table(p).to_pylist() for p in (root / "a/evidence/demo").glob("*.parquet")}
    assert len(rows["cses"]) == 8
    assert len({r["sector"] for r in rows["cses"]}) >= 2
    assert len({r["peer_group"] for r in rows["cses"]}) >= 2
    for name, minimum in {"alerts": 5000, "cases": 500, "assets": 100, "investigation_events": 1000, "escalations": 100}.items():
        assert len(rows[name]) >= minimum
    assert {r["timestamp"].month for r in rows["alerts"]} == set(range(1, 13))
    indexes = {kind: {(r["cse_id"], r[key]): r for r in rows[kind]} for kind, key in {"assets": "asset_id", "cases": "case_id", "alerts": "alert_id"}.items()}
    for alert in rows["alerts"]:
        assert (alert["cse_id"], alert["asset_id"]) in indexes["assets"]
        assert (alert["cse_id"], alert["case_id"]) in indexes["cases"]
    for event in rows["investigation_events"]:
        case = indexes["cases"][(event["cse_id"], event["case_id"])]
        assert case["opened_at"] <= event["timestamp"] <= case["closed_at"]
    for escalation in rows["escalations"]:
        alert = indexes["alerts"][(escalation["cse_id"], escalation["alert_id"])]
        assert escalation["timestamp"] == alert["escalation_timestamp"]
    for artifact in manifest.artifacts:
        assert artifact.row_count == len(rows[artifact.filename.removesuffix(".parquet")])


def test_ground_truth_is_separate_and_scenarios_have_evidence(generated):
    root, *_ = generated
    labels = json.loads((root / "a/labels/demo/labels.json").read_text())
    scenarios = {label["scenario"] for label in labels}
    assert scenarios == {"fast_closure", "recurring_alerts", "missing_escalation", "missing_monitoring", "template_repetition", "low_activity", "peer_deviation", "closure_bursts", "metric_evidence_mismatch", "healthy_control"}
    assert all(label["evidence"] for label in labels)
    assert {label["cse_id"] for label in labels if label["scenario"] == "healthy_control"} == {"CSE-04"}
    assert not any(label["cse_id"] == "CSE-04" and label["scenario"] != "healthy_control" for label in labels)
    for path in (root / "a/evidence/demo").glob("*.parquet"):
        assert not {"label", "scenario", "ground_truth"} & set(pq.read_schema(path).names)


def test_injected_patterns_are_observable_in_records(generated):
    root, *_ = generated
    base = root / "a/evidence/demo"
    alerts = pq.read_table(base / "alerts.parquet").to_pylist()
    cases = pq.read_table(base / "cases.parquet").to_pylist()
    labels = json.loads((root / "a/labels/demo/labels.json").read_text())
    index = {("alerts", a["cse_id"], a["alert_id"]): a for a in alerts}
    index.update({("cases", c["cse_id"], c["case_id"]): c for c in cases})
    for label in labels:
        for ref in label["evidence"]:
            if label["scenario"] == "fast_closure":
                a = index[(ref["record_type"], label["cse_id"], ref["record_id"])]
                assert a["severity"] in ("critical", "high")
                assert (a["closure_timestamp"] - a["timestamp"]).total_seconds() <= 900
            if label["scenario"] == "missing_escalation":
                a = index[(ref["record_type"], label["cse_id"], ref["record_id"])]
                assert a["escalation_required"] and a["escalation_timestamp"] is None
            if label["scenario"] == "missing_monitoring":
                assert not any(a["cse_id"] == label["cse_id"] and a["asset_id"] == ref["record_id"] for a in alerts)
    healthy = [a for a in alerts if a["cse_id"] == "CSE-04" and a["severity"] in ("high", "critical")]
    assert healthy and all(a["escalation_timestamp"] is not None for a in healthy)


def test_generator_refuses_labels_inside_evidence(tmp_path):
    make = generator()
    with pytest.raises(ValueError, match="separate"):
        make(1, tmp_path / "demo", tmp_path / "demo/labels")


def test_generator_can_create_a_distinct_earlier_assessment(tmp_path):
    from sat_sa.synthetic.generator import build_records
    older, _ = build_records(7, assessment_year=2024)
    current, _ = build_records(7)
    assert older['cses'][0].assessment_period.end <= current['cses'][0].assessment_period.start
    assert older['alerts'][0].timestamp.year == 2024
    assert current['alerts'][0].timestamp.year == 2025


def test_generator_never_overwrites(generated):
    root, *_ = generated
    before = hashes(root / "a")
    with pytest.raises(FileExistsError):
        generator()(20260928, root / "a/evidence/demo", root / "a/labels/demo")
    assert before == hashes(root / "a")


def test_invalid_label_destination_does_not_publish_evidence(tmp_path):
    make = generator()
    blocked = tmp_path / "blocked"
    blocked.write_text("file instead of directory")
    with pytest.raises(OSError):
        make(1, tmp_path / "evidence/demo", blocked / "labels")
    assert not (tmp_path / "evidence/demo").exists()
