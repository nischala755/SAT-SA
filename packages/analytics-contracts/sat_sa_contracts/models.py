"""Canonical contracts. Missing evidence is nullable, invalid evidence is rejected."""
from typing import Annotated, Any, Literal, Self

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

from .enums import ReviewOutcome, Role, Severity

Identifier = Annotated[str, Field(min_length=1, max_length=160, pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$")]
Text = Annotated[str, Field(min_length=1, max_length=2000)]
Count = Annotated[int, Field(ge=0, strict=True)]
Ratio = Annotated[float, Field(ge=0, le=1)]
Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)


class AssessmentPeriod(Contract):
    start: AwareDatetime
    end: AwareDatetime

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.end <= self.start:
            raise ValueError("assessment end must follow start (exclusive)")
        return self


class Provenance(Contract):
    source_file: Text
    source_record: Text
    ingestion_batch: Identifier
    transformation_version: Text


class EntityRecord(Contract):
    cse_id: Identifier
    provenance: Provenance


def check_order(*timestamps: AwareDatetime | None) -> None:
    present = [t for t in timestamps if t is not None]
    if any(a > b for a, b in zip(present, present[1:])):
        raise ValueError("lifecycle timestamps are reversed")


class CSE(EntityRecord):
    name: Text
    sector: Text
    peer_group: Text
    criticality: Severity
    assessment_period: AssessmentPeriod
    entity_size: Literal["small", "medium", "large"] = "medium"


class Alert(EntityRecord):
    alert_id: Identifier
    timestamp: AwareDatetime
    severity: Severity
    source: Text
    alert_category: Text
    rule_use_case: Text
    asset_id: Identifier | None = None
    asset_criticality: Severity | None = None
    acknowledgement_timestamp: AwareDatetime | None = None
    investigation_start_timestamp: AwareDatetime | None = None
    case_id: Identifier | None = None
    disposition: Text | None = None
    closure_timestamp: AwareDatetime | None = None
    closure_reason: Text | None = None
    escalation_required: bool | None = None
    escalation_timestamp: AwareDatetime | None = None
    escalation_type: Text | None = None

    @model_validator(mode="after")
    def lifecycle(self) -> Self:
        check_order(self.timestamp, self.acknowledgement_timestamp, self.investigation_start_timestamp, self.closure_timestamp)
        check_order(self.timestamp, self.escalation_timestamp, self.closure_timestamp)
        return self


class Case(EntityRecord):
    case_id: Identifier
    opened_at: AwareDatetime
    closed_at: AwareDatetime | None = None
    severity: Severity
    assigned_team: Text | None = None
    investigator: Text | None = None
    investigation_steps_count: Count | None = None
    investigation_duration: Annotated[float, Field(ge=0)] | None = None  # minutes
    escalation_status: Text | None = None
    escalation_timestamp: AwareDatetime | None = None
    root_cause: Text | None = None
    remediation_status: Text | None = None
    linked_alert_count: Count | None = None
    closure_reason: Text | None = None

    @model_validator(mode="after")
    def lifecycle(self) -> Self:
        check_order(self.opened_at, self.escalation_timestamp, self.closed_at)
        return self


class Asset(EntityRecord):
    asset_id: Identifier
    criticality: Severity
    environment: Text
    system_type: Text
    monitoring_expected: bool
    monitoring_source: Text | None = None


class InvestigationEvent(EntityRecord):
    event_id: Identifier
    case_id: Identifier
    timestamp: AwareDatetime
    event_type: Text
    actor_team: Text
    action: Text
    evidence_reference: Text | None = None
    notes_length: Count | None = None
    outcome: Text | None = None


class EscalationRecord(EntityRecord):
    escalation_id: Identifier
    alert_id: Identifier
    case_id: Identifier | None = None
    timestamp: AwareDatetime
    escalation_type: Text
    receiving_team: Text


class Artifact(Contract):
    filename: Annotated[str, Field(pattern=r"^[a-z_]+\.parquet$")]
    sha256: Digest
    row_count: Count


class DatasetVersion(Contract):
    dataset_id: Identifier
    dataset_hash: Digest
    schema_version: Text
    generator_version: Text | None = None
    seed: Count | None = None
    created_at: AwareDatetime
    assessment_period: AssessmentPeriod
    artifacts: tuple[Artifact, ...]


class DatasetManifest(DatasetVersion):
    pass


class AnalyticsRun(Contract):
    run_id: Identifier
    dataset_id: Identifier
    dataset_hash: Digest
    analytics_version: Text
    software_version: Text
    configuration: dict[str, Any]
    configuration_hash: Digest
    assessment_period: AssessmentPeriod
    started_at: AwareDatetime
    completed_at: AwareDatetime | None = None
    status: Literal["queued", "running", "completed", "failed"]
    records_analysed: Count = 0
    findings_generated: Count = 0
    execution_seconds: Annotated[float, Field(ge=0)] | None = None

    @model_validator(mode="after")
    def lifecycle(self) -> Self:
        check_order(self.started_at, self.completed_at)
        return self


class EvidenceReference(Contract):
    dataset_id: Identifier
    cse_id: Identifier
    record_type: Literal["cses", "alerts", "cases", "assets", "investigation_events", "escalations"]
    record_id: Identifier
    provenance: Provenance


class SupervisorySignal(Contract):
    signal_id: Identifier
    run_id: Identifier
    cse_id: Identifier
    name: Text
    category: Literal["detection", "investigation", "escalation", "incident_response", "security_operations", "governance", "operational_discipline", "cyber_resilience"]
    description: Text
    severity: Severity
    signal_strength: Literal["low", "medium", "high"]
    confidence: Literal["limited", "medium", "high"]
    data_completeness: Ratio
    evidence_count: Count
    methodology: Text
    thresholds: dict[str, Any]
    observed_evidence: Text
    inferred_signal: Text
    supervisory_hypothesis: Text
    evidence_references: tuple[EvidenceReference, ...]
    calculation_version: Text


class ReviewDecision(Contract):
    decision_id: Identifier
    signal_id: Identifier
    cse_id: Identifier
    actor: Text
    role: Role
    timestamp: AwareDatetime
    outcome: ReviewOutcome
    note: Annotated[str, Field(max_length=4000)] = ""

    @model_validator(mode="after")
    def authorized_role(self) -> Self:
        if self.role == Role.reader:
            raise ValueError("reader cannot record a supervisory decision")
        return self


class AuditEvent(Contract):
    event_id: Identifier
    timestamp: AwareDatetime
    actor: Text
    role: Role
    action: Text
    object_id: Text
    details: dict[str, Any] = Field(default_factory=dict)


class HealthStatus(Contract):
    status: Literal["ok", "unavailable"]
    service: Literal["sat-sa-api"] = "sat-sa-api"
    software_version: str = "0.1.0"
    demo_mode: bool
    storage_ready: bool
    registered_datasets: Count | None
    message: str


RECORD_MODELS = {"cses": CSE, "alerts": Alert, "cases": Case, "assets": Asset,
                 "investigation_events": InvestigationEvent, "escalations": EscalationRecord}
RECORD_KEYS = {"cses": "cse_id", "alerts": "alert_id", "cases": "case_id", "assets": "asset_id",
               "investigation_events": "event_id", "escalations": "escalation_id"}
