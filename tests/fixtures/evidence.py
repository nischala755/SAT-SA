from sat_sa_contracts.models import CSE, Alert, Asset, AssessmentPeriod, Provenance


def small_records():
    provenance = Provenance(source_file="fixture.json", source_record="1", ingestion_batch="B1", transformation_version="1")
    return {
        "cses": [CSE(cse_id="E1", name="Entity one", sector="energy", peer_group="energy-medium", criticality="critical", assessment_period=AssessmentPeriod(start="2025-01-01T00:00:00Z", end="2026-01-01T00:00:00Z"), provenance=provenance)],
        "assets": [Asset(cse_id="E1", asset_id="AS1", criticality="critical", environment="production", system_type="server", monitoring_expected=True, provenance=provenance)],
        "alerts": [Alert(cse_id="E1", alert_id="A1", asset_id="AS1", severity="critical", timestamp="2025-03-01T12:00:00Z", source="EDR", alert_category="endpoint", rule_use_case="change", escalation_required=True, provenance=provenance)],
        "cases": [], "investigation_events": [], "escalations": [],
    }
