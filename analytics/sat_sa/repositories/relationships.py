"""Referential checks for normalized synthetic datasets, always entity scoped."""
from sat_sa_contracts.models import RECORD_KEYS, RECORD_MODELS


def validate_records(records: dict) -> dict:
    if set(records) != set(RECORD_MODELS):
        raise ValueError("Evidence tables must exactly match the normalized contract")
    validated = {}
    indexes = {}
    for kind, model in RECORD_MODELS.items():
        rows = [model.model_validate_json(row.model_dump_json()) for row in records[kind]]
        rows.sort(key=lambda row: (row.cse_id, getattr(row, RECORD_KEYS[kind])))
        index = {(row.cse_id, getattr(row, RECORD_KEYS[kind])): row for row in rows}
        if len(index) != len(rows):
            raise ValueError(f"Duplicate entity-scoped identifier in {kind}")
        validated[kind], indexes[kind] = rows, index
    entities = {c.cse_id: c for c in validated["cses"]}
    if not entities:
        raise ValueError("At least one CSE is required")
    for rows in validated.values():
        for row in rows:
            if row.cse_id not in entities:
                raise ValueError("Unknown CSE reference")
    for alert in validated["alerts"]:
        period = entities[alert.cse_id].assessment_period
        if not period.start <= alert.timestamp < period.end:
            raise ValueError("Alert outside assessment period")
        if alert.asset_id is not None and (alert.cse_id, alert.asset_id) not in indexes["assets"]:
            raise ValueError("Unresolved entity-scoped asset reference")
        if alert.case_id is not None and (alert.cse_id, alert.case_id) not in indexes["cases"]:
            raise ValueError("Unresolved entity-scoped case reference")
    for event in validated["investigation_events"]:
        case = indexes["cases"].get((event.cse_id, event.case_id))
        if case is None:
            raise ValueError("Unresolved entity-scoped case reference")
        if event.timestamp < case.opened_at or (case.closed_at is not None and event.timestamp > case.closed_at):
            raise ValueError("Investigation event outside case lifecycle")
    for escalation in validated["escalations"]:
        alert = indexes["alerts"].get((escalation.cse_id, escalation.alert_id))
        if alert is None or alert.case_id != escalation.case_id:
            raise ValueError("Unresolved entity-scoped escalation reference")
        if escalation.timestamp != alert.escalation_timestamp:
            raise ValueError("Escalation timestamp disagrees with alert")
    return validated
