"""Versioned, validated rule thresholds; prototype defaults are not legal standards."""
from pathlib import Path
from typing import Annotated,Literal
from pydantic import Field
from sat_sa_contracts.models import Contract

Positive=Annotated[int,Field(gt=0,strict=True)]
class EngineConfig(Contract):
    version:Literal['1.0.0']
    minimum_sample:Positive
    minimum_peers:Annotated[int,Field(ge=3,strict=True)]
    fast_minutes:Positive
    short_investigation_minutes:Positive
    minimum_investigation_events:Positive
    recurrence_days:Positive
    recurrence_count:Annotated[int,Field(ge=2,strict=True)]
    burst_count:Annotated[int,Field(ge=2,strict=True)]
    concentration_ratio:Annotated[float,Field(gt=0,le=1)]
    long_case_days:Positive
    low_activity_ratio:Annotated[float,Field(gt=0,lt=1)]
    peer_deviation_multiplier:Annotated[float,Field(gt=1)]
    missingness_ratio:Annotated[float,Field(gt=0,le=1)]
    expected_categories:Annotated[list[str],Field(min_length=1)]
    expected_escalation_severities:list[Literal['critical','high','medium','low','informational']]
    metric_integrity_enabled:bool

def load_engine():
    return EngineConfig.model_validate_json((Path(__file__).resolve().parents[3]/'config/engine.json').read_text()).model_dump()
