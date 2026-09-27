# Completion ledger

2026-09-27: User authorized remaining phases and optional Mistral after approving local summary design. Existing dedicated branch retained. Planning approval stops are superseded by explicit instruction to execute through completion.

Ruling: Mistral is an explicitly enabled external summary provider, never an analytics dependency. Cost: enabling it sends selected evidence to Mistral; CLI requires cloud consent and deployment policy must permit this. Default remains local/offline.

Summary: 6 initial tests passed and actual Qwen generation succeeded. Provider malformed-response regression found AttributeError on non-object JSON; fixed with explicit shape checks, 10 tests passed. Mistral live request returned HTTP 429; no successful Mistral inference claimed.

Ingestion: CSV/JSON mapping, provenance, missingness and relationship checks passed 5 tests. Internal REST adapter default-disabled with fixed private-IP URL passed 5 tests. Initial ingestion RED run completed after implementation due asynchronous timing; no claim of an observed RED result for that task.

Analytics: 5 engine tests and 7 predicate tests passed; all eight families compute actual data-derived indicators. Review queue deduplicates entity-scoped samples. Validation is post-run only and includes explicit denominators.

Workflow: persistent jobs/results/reviews and API permissions passed initial tests; full suite at first integration milestone passed 77 tests. Browser shell/outage and overview→evidence→decision→audit passed 3 tests. Native production and both Docker image builds succeeded.

Ruling: prototype analysis is bounded to 100,000 records and uploads to 10,000 records/2 MB per file. This is an explicit scalability limitation, not a million-record readiness claim. Cost: larger submissions require further SQL/streaming implementation and benchmarks.

Ruling: existing canonical records require referenced entities/assets/cases to resolve correctly; uploads reject unresolved non-null references. Null optional evidence remains representable. Cost: incomplete linked exports must either include referenced records or explicitly represent missing links as null.

Independent final review: six Important findings accepted. Regression suite reproduced all six backend cases (including separate recovery/history cases) RED, then GREEN: uncapped job recovery/history; eligible escalation population; CSV parser failures; matched assessment windows; rule-specific completeness. Browser regression reproduced missing selected source, then passed after queue selection/reference pagination fixes. No Critical findings.

Final: Ruling: sector selection graded Important rather than Minor because imported non-demo sectors could not be selected. Changed to an exact-name input. Cost: free-text spelling must match the stored sector; no dropdown convenience.

Final: Ruling: reviewer declined million-record readiness; bounded scale remains explicit and is not claimed. Cost: large operational workloads need another implementation/benchmark stage.

Final: Ruling: live Mistral success and egress-denied Qwen remain externally blocked/unverified respectively; tests do not substitute for successful live verification. Cost: provider quota and separate isolated model deployment must be resolved before relying on these modes.

Final: Ruling: model sentence-level grounding is not certified; original records accompany every untrusted draft for human checking. Cost: examiners must verify every material statement.

Final: Ruling: final documentation/container evidence was pending at review and is verified in the delivery pass. Cost if omitted: deployment claims would be unsupported; completion report records actual outcomes.

Additional final correctness check: full-run overview aggregates now independent of the 25-entity display page and 100-row trend API page; a 30-entity regression failed before implementation and passes afterward.
