# Completion ledger

2026-09-27: User authorized remaining phases and optional Mistral after approving local summary design. Existing dedicated branch retained. Planning approval stops are superseded by explicit instruction to execute through completion.

Ruling: Mistral is an explicitly enabled external summary provider, never an analytics dependency. Cost: enabling it sends selected evidence to Mistral; CLI requires cloud consent and deployment policy must permit this. Default remains local/offline.

Summary: 6 initial tests passed and actual Qwen generation succeeded. Provider malformed-response regression found AttributeError on non-object JSON; fixed with explicit shape checks, 10 tests passed. Mistral live request returned HTTP 429; no successful Mistral inference claimed.

Ingestion: CSV/JSON mapping, provenance, missingness and relationship checks passed 5 tests. Internal REST adapter default-disabled with fixed private-IP URL passed 5 tests. Initial ingestion RED run completed after implementation due asynchronous timing; no claim of an observed RED result for that task.

Analytics: 5 engine tests and 7 predicate tests passed; all eight families compute actual data-derived indicators. Review queue deduplicates entity-scoped samples. Validation is post-run only and includes explicit denominators.

Workflow: persistent jobs/results/reviews and API permissions passed initial tests; full suite at first integration milestone passed 77 tests. Browser shell/outage and overview→evidence→decision→audit passed 3 tests. Native production and both Docker image builds succeeded.

Ruling: prototype analysis is bounded to 100,000 records and uploads to 10,000 records/2 MB per file. This is an explicit scalability limitation, not a million-record readiness claim. Cost: larger submissions require further SQL/streaming implementation and benchmarks.

Ruling: existing canonical records require referenced entities/assets/cases to resolve correctly; uploads reject unresolved non-null references. Null optional evidence remains representable. Cost: incomplete linked exports must either include referenced records or explicitly represent missing links as null.
