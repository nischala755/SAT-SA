"""Seeded, entirely local synthetic evidence; no signal calculation or label reads."""
import random
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sat_sa_contracts.models import (
    Alert, AssessmentPeriod, Asset, CSE, Case, EscalationRecord,
    InvestigationEvent, Provenance, RECORD_MODELS,
)
from sat_sa.repositories.parquet_evidence import ParquetEvidenceRepository, canonical_json
from .scenarios import SCENARIOS

def build_records(seed: int, assessment_year: int = 2025):
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError("Seed must be a nonnegative integer")
    if isinstance(assessment_year, bool) or not isinstance(assessment_year, int) or not 2000 <= assessment_year <= 2100:
        raise ValueError("Assessment year must be between 2000 and 2100")
    period = AssessmentPeriod(start=datetime(assessment_year, 1, 1, tzinfo=timezone.utc), end=datetime(assessment_year + 1, 1, 1, tzinfo=timezone.utc))
    rng = random.Random(seed)
    records = {kind: [] for kind in RECORD_MODELS}
    labels = {}

    def provenance(kind, record_id):
        return Provenance(source_file=f"{kind}.parquet", source_record=record_id, ingestion_batch=f"synthetic-{seed}", transformation_version="1.0.0")

    def label(scenario, entity, kind, record_id):
        key = (scenario, entity)
        labels.setdefault(key, {"scenario": scenario, "cse_id": entity, "description": SCENARIOS[scenario], "evidence": []})["evidence"].append({"record_type": kind, "record_id": record_id})

    for entity_number in range(1, 9):
        entity = f"CSE-{entity_number:02d}"
        sector = "energy" if entity_number <= 4 else "financial_services"
        records["cses"].append(CSE(cse_id=entity, name=f"Synthetic {sector.replace('_', ' ').title()} Entity {entity_number:02d}", sector=sector, peer_group=f"{sector}-medium-critical", criticality="critical", assessment_period=period, provenance=provenance("cses", entity)))
        for i in range(24):
            asset_id = f"AS-{i:03d}"  # Deliberately entity-local IDs exercise composite keys.
            criticality = "critical" if i < 8 else "medium"
            records["assets"].append(Asset(cse_id=entity, asset_id=asset_id, criticality=criticality, environment="production", system_type="control_server" if sector == "energy" else "application_server", monitoring_expected=True, monitoring_source="EDR", provenance=provenance("assets", asset_id)))
            if entity_number == 2 and 4 <= i < 8:
                label("missing_monitoring", entity, "assets", asset_id)
        if entity_number in (4, 6):
            label("healthy_control" if entity_number == 4 else "low_activity", entity, "cses", entity)
        for month in range(1, 13):
            count = 1 if entity_number == 6 else 10
            for j in range(count):
                case_id = f"C-{month:02d}-{j:03d}"
                severity = rng.choices(["critical", "high", "medium", "low"], [15, 25, 40, 20])[0]
                opened = datetime(assessment_year, month, 2 + j * 2, rng.randrange(6, 20), rng.randrange(60), tzinfo=timezone.utc)
                duration = rng.randrange(60, 181)
                steps = rng.randrange(3, 7)
                reason = rng.choice(["Reviewed correlated evidence and resolved", "Documented benign activity verified", "Remediation completed and verified", "Root cause addressed; follow-up recorded"])
                fast = entity_number == 1 and month >= 7 and j < 3
                repeated = entity_number == 2 and j < 4
                template = entity_number == 3 and j < 4
                burst = entity_number == 5 and j < 6
                deviation = entity_number == 7 and j < 5
                mismatch = entity_number == 8 and j < 6
                if fast or mismatch:
                    severity, duration = "critical", 7
                    steps = 1 if fast else 0
                if template:
                    steps, reason = 1, "Standard review completed"
                if burst:
                    closed = datetime(assessment_year, month, 28, 18, tzinfo=timezone.utc)
                    opened = closed - timedelta(minutes=duration)
                if deviation:
                    duration = rng.randrange(720, 1441)
                closed = opened + timedelta(minutes=duration)
                expected = severity in ("critical", "high")
                escalated = opened + timedelta(minutes=3) if expected and not (fast or mismatch) else None
                records["cases"].append(Case(cse_id=entity, case_id=case_id, opened_at=opened, closed_at=closed, severity=severity, assigned_team=f"Team-{j % 3 + 1}", investigator=f"Analyst-{j % 5 + 1}", investigation_steps_count=steps, investigation_duration=duration, escalation_status="recorded" if escalated else ("not_supplied" if expected else "not_required"), escalation_timestamp=escalated, root_cause=None if repeated or mismatch else "Synthetic cause documented", remediation_status=None if repeated or mismatch else "completed", linked_alert_count=8, closure_reason=reason, provenance=provenance("cases", case_id)))
                for scenario, enabled in [("template_repetition", template), ("closure_bursts", burst), ("peer_deviation", deviation), ("metric_evidence_mismatch", mismatch)]:
                    if enabled:
                        label(scenario, entity, "cases", case_id)
                for k in range(steps):
                    event_id = f"I-{month:02d}-{j:03d}-{k}"
                    action = "Standard checklist reviewed" if template else ["Correlate alert evidence", "Inspect affected asset", "Validate root cause", "Verify remediation", "Peer review", "Record closure approval"][k]
                    records["investigation_events"].append(InvestigationEvent(cse_id=entity, event_id=event_id, case_id=case_id, timestamp=opened + timedelta(minutes=duration * (k + 1) / (steps + 1)), event_type="investigation_step", actor_team=f"Team-{j % 3 + 1}", action=action, evidence_reference=f"local:{case_id}:{k}", notes_length=24 if template else rng.randrange(100, 801), outcome="Step recorded", provenance=provenance("investigation_events", event_id)))
                allowed_assets = [i for i in range(24) if not (entity_number == 2 and 4 <= i < 8)]
                for k in range(8):
                    alert_id = f"A-{month:02d}-{j:03d}-{k}"
                    asset_index = 0 if repeated else allowed_assets[(month * 80 + j * 8 + k) % len(allowed_assets)]
                    timestamp = opened + timedelta(seconds=10 * k)
                    category = "endpoint" if repeated else rng.choice(["endpoint", "identity", "network"])
                    records["alerts"].append(Alert(cse_id=entity, alert_id=alert_id, timestamp=timestamp, severity=severity, source="EDR", alert_category=category, rule_use_case=f"{category}-review", asset_id=f"AS-{asset_index:03d}", asset_criticality="critical" if asset_index < 8 else "medium", acknowledgement_timestamp=timestamp + timedelta(seconds=30), investigation_start_timestamp=None if mismatch else timestamp + timedelta(seconds=45), case_id=case_id, disposition="resolved", closure_timestamp=closed, closure_reason=reason, escalation_required=expected, escalation_timestamp=escalated, escalation_type="supervisor" if escalated else None, provenance=provenance("alerts", alert_id)))
                    if escalated:
                        esc_id = f"ESC-{month:02d}-{j:03d}-{k}"
                        records["escalations"].append(EscalationRecord(cse_id=entity, escalation_id=esc_id, alert_id=alert_id, case_id=case_id, timestamp=escalated, escalation_type="supervisor", receiving_team="Duty supervisor", provenance=provenance("escalations", esc_id)))
                    for scenario, enabled in [("fast_closure", fast), ("missing_escalation", expected and not escalated), ("recurring_alerts", repeated)]:
                        if enabled:
                            label(scenario, entity, "alerts", alert_id)
    return records, [labels[key] for key in sorted(labels)]


def generate_dataset(seed: int, output: Path, labels_output: Path, assessment_year: int = 2025):
    output, labels_output = Path(output).resolve(), Path(labels_output).resolve()
    # Sibling trees are required; both nesting directions would leak labels.
    if output == labels_output or output in labels_output.parents or labels_output in output.parents:
        raise ValueError("Ground-truth labels must be in a separate tree")
    if output.exists() or labels_output.exists():
        raise FileExistsError("Synthetic evidence and labels are immutable")
    records, labels = build_records(seed, assessment_year)
    # Prepare labels before publishing evidence so invalid/unwritable label paths
    # cannot leave a completed evidence version from a failed generation.
    labels_output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".labels-staging-", dir=labels_output.parent) as temporary:
        staged_labels = Path(temporary)
        (staged_labels / "labels.json").write_bytes(canonical_json(labels))
        manifest = ParquetEvidenceRepository(output.parent).write_dataset(records, output, seed=seed)
        staged_labels.rename(labels_output)
        return manifest
