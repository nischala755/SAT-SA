"""Explicit local configuration. Phase 1 is a synthetic-data demo only."""
import json
import os
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, model_validator
from sat_sa_contracts.models import Contract, Count


class Settings(Contract):
    storage_root: Path = Path("runtime")
    demo_mode: bool = True
    demo_seed: Count = 20260927

    @model_validator(mode="after")
    def demo_only(self):
        if not self.demo_mode:
            raise ValueError("Production authentication is not implemented in Phase 1; demo_mode must be true")
        return self


class AnalyticsConfig(Contract):
    version: Literal["1.0.0"]
    severity_mappings: dict[str, str]
    minimum_peer_entities: Annotated[int, Field(ge=3)]
    minimum_sample_size: Annotated[int, Field(ge=1)]
    fast_closure_minutes: Annotated[int, Field(gt=0)]
    recurrence_window_days: Annotated[int, Field(gt=0)]
    escalation_expected_severities: list[str]
    monitoring_expected_criticalities: list[str]
    expected_categories: list[str]


def load_settings(path: Path | None = None) -> Settings:
    values = json.loads(path.read_text(encoding="utf-8")) if path else {}
    for field in Settings.model_fields:
        value = os.environ.get("SAT_SA_" + field.upper())
        if value is not None:
            if field == "demo_seed":
                value = int(value)
            values[field] = value
    return Settings.model_validate(values)


def load_analytics_config(path: Path | None = None) -> AnalyticsConfig:
    path = path or Path(os.environ.get("SAT_SA_CONFIG", "config/defaults.json"))
    return AnalyticsConfig.model_validate_json(path.read_text(encoding="utf-8"))
