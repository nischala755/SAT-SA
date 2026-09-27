from datetime import datetime, timezone
import importlib

import pytest
from pydantic import ValidationError


def models():
    try:
        return importlib.import_module("sat_sa_contracts.models")
    except ModuleNotFoundError:
        pytest.fail("Canonical domain models have not been implemented")


def alert_data():
    return dict(alert_id="A1", cse_id="E1", timestamp="2025-01-01T00:00:00Z",
                severity="critical", source="EDR", alert_category="endpoint",
                rule_use_case="endpoint-change", asset_id="AS1",
                provenance=dict(source_file="alerts.csv", source_record="1", ingestion_batch="B1", transformation_version="1"))


@pytest.mark.parametrize("name", ["CSE", "Alert", "Case", "Asset", "InvestigationEvent", "DatasetVersion", "AnalyticsRun", "SupervisorySignal", "EvidenceReference", "ReviewDecision"])
def test_required_contracts(name):
    assert getattr(models(), name).model_json_schema()["type"] == "object"


@pytest.mark.parametrize("changes", [
    {"severity": "urgent"}, {"unknown": 1}, {"timestamp": "2025-01-01T00:00:00"},
    {"timestamp": "not-a-date"}, {"closure_timestamp": "2024-12-31T23:59:00Z"},
    {"acknowledgement_timestamp": "2024-12-31T23:59:00Z"},
    {"investigation_start_timestamp": "2024-12-31T23:59:00Z"},
    {"escalation_timestamp": "2024-12-31T23:59:00Z"},
    {"acknowledgement_timestamp": "2025-01-01T00:05:00Z", "investigation_start_timestamp": "2025-01-01T00:04:00Z"},
    {"closure_timestamp": "2025-01-01T00:05:00Z", "investigation_start_timestamp": "2025-01-01T00:06:00Z"},
    {"closure_timestamp": "2025-01-01T00:05:00Z", "escalation_timestamp": "2025-01-01T00:06:00Z"},
])
def test_alert_rejects_invalid_lifecycle(changes):
    cls = models().Alert
    with pytest.raises(ValidationError):
        cls(**(alert_data() | changes))


def test_missing_evidence_is_not_invalid():
    alert = models().Alert(**alert_data(), escalation_required=True)
    assert alert.escalation_timestamp is None
    assert alert.case_id is None
    assert alert.timestamp == datetime(2025, 1, 1, tzinfo=timezone.utc)


@pytest.mark.parametrize("changes", [
    {"closed_at": "2024-01-01T00:00:00Z"}, {"investigation_steps_count": -1},
    {"investigation_duration": -0.1}, {"escalation_timestamp": "2024-01-01T00:00:00Z"},
    {"closed_at": "2025-01-01T01:00:00Z", "escalation_timestamp": "2025-01-01T02:00:00Z"},
])
def test_case_validation(changes):
    cls = models().Case
    with pytest.raises(ValidationError):
        cls(**(dict(case_id="C1", cse_id="E1", opened_at="2025-01-01T00:00:00Z", severity="high", provenance=alert_data()["provenance"]) | changes))


def test_period_must_be_ordered():
    cls = models().AssessmentPeriod
    with pytest.raises(ValidationError):
        cls(start="2025-02-01T00:00:00Z", end="2025-01-01T00:00:00Z")
