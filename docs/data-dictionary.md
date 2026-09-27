# Phase 1 data dictionary

Canonical definitions are Pydantic models in `packages/analytics-contracts/sat_sa_contracts/models.py`. Generated JSON schemas live in `data/schemas`; TypeScript types in `packages/shared-types/src/generated.ts`. Run `python scripts/export_contracts.py --check` to reject drift.

All timestamps include an offset; synthetic timestamps use UTC. Assessment periods are start-inclusive/end-exclusive. Durations use minutes. Counts cannot be negative. Missing investigation, closure and escalation evidence is represented by null, not a fabricated zero. Unknown fields and invalid/reversed lifecycles fail validation. Missing escalation evidence does not imply an escalation never occurred.

| Record | Entity-scoped identity | Purpose |
| --- | --- | --- |
| CSE | cse_id | Pseudonym, sector, peer group, criticality, size and period |
| Asset | cse_id + asset_id | Inventory, environment, type and monitoring expectation |
| Alert | cse_id + alert_id | Alert lifecycle, disposition, case, asset and escalation evidence |
| Case | cse_id + case_id | Investigation summary, team, investigator, root cause and remediation |
| InvestigationEvent | cse_id + event_id | Timestamped action, evidence pointer and notes length; no raw notes |
| EscalationRecord | cse_id + escalation_id | Explicit linked escalation evidence |
| DatasetVersion | dataset_id | Immutable hashes, artifact counts, period and versions |
| AnalyticsRun | run_id | Future execution/configuration audit contract; no runs created in Phase 1 |
| SupervisorySignal | signal_id + run_id | Future evidence-backed indicator contract; no signals created |
| EvidenceReference | dataset + entity + record type + record ID | Traceable source reference |
| ReviewDecision | decision_id | Future human decision contract; no decisions created |
| AuditEvent | event_id | Append-only local action record |

Every input record includes source filename, source record ID, ingestion batch and transformation version. Synthetic source files are the generated Parquet tables; source record IDs correspond to entity-scoped record IDs. Source provenance represents generated evidence, not an asserted real SOC submission.

Dataset `created_at` is the deterministic synthetic snapshot timestamp (assessment period end). Actual registration time is recorded separately in the metadata audit. Registration/audit timestamps are intentionally not part of reproducible dataset artifacts.

Ground truth lives in `data/ground_truth/demo/labels.json` and is excluded from all evidence repository table selections and API routes. Labels describe known injections; they are not calculated findings or measured analytics performance.
