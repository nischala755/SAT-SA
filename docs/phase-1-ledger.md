# Execution ledger — docs/superpowers/plans/2026-09-27-phase-1.md

Authorization: plan approved; implement Phase 1 in this workspace; stop after verification report.

Pre-flight: models → repository → generator → API share canonical Pydantic models. API health and frontend share generated HealthStatus. No conflicting interfaces found.

Ruling: use the approved empty workspace directly, without a second worktree; no existing Git branch or code exists to isolate. Initialize a local phase-1 branch for review only. Cost if wrong: workspace placement changes, not product behavior.

Ruling: use a checked-in execution ledger and PowerShell command recorder instead of the skill's Bash bookkeeping helpers on this Windows host. Preserve command logs and final report rather than deleting verification evidence. Cost if wrong: no runtime impact; review tooling is different.

Initial environment probe: Python 3.12.10, Node v24.18.0, npm 11.16.0, Docker CLI 29.6.1, Compose v5.1.4. `docker info` exited 1: dockerDesktopLinuxEngine named pipe not found.

Tasks: 1 models/configuration pending; 2 persistence pending; 3 generator pending; 4 application pending; 5 packaging/verification pending.

Task 1: complete — 34 tests pass; 20 generated contract artifacts pass freshness. RED: 34 explicit missing-feature failures. An earlier venv test invocation failed because installation was still running; not counted as RED evidence.

Task 2 debugging: fixed Windows open-lock cleanup and normalized Path input at the repository boundary. Remaining integration failure identified DuckDB's timestamp conversion runtime dependency on pytz.

Ruling: add pytz as an explicit dependency because DuckDB's timezone-aware Python fetch requires it. Cost if wrong: a small unnecessary local dependency; no network calls at runtime.

Task 2: complete — full suite 44 passed, including separate-process persistence. RED: ten missing repository failures. Windows/path defects and pytz dependency fixed without relaxing assertions.

Task 3: complete — full suite 50 passed. Generator tests prove deterministic logical rows, evidence/label hashes, changed-seed differences, record links, 12 months, all ten labelled scenarios and healthy-control escalation evidence. No analytical outputs are generated.

Ruling: use one API process as the serialized metadata owner in Phase 1; demo bootstrap runs before that process. A background job worker is deferred because Phase 1 has no ingestion/analytics jobs. Cost if wrong: future jobs need the already-planned single-writer service coordination.

Task 4 checks: Python 55 passed (one upstream Starlette/httpx deprecation warning); frontend 5 passed; TypeScript and production build passed; actual native frontend→backend request passed. Browser failure assertion initially matched Next.js's built-in route announcer as well as the application alert; scoped the assertion to main without weakening its expected message. Native start adjusted to use generated standalone server after Next.js's explicit warning.

Task 4: complete — 2/2 browser tests pass against the native standalone server, including failure/retry. Local resources only observed.

Ruling: Docker Desktop 29.6.1 does not publish requested host ports on an internal-only network (healthy services, empty NetworkSettings.Ports, localhost connection refused). Use a standard bridge with loopback host ports for normal Compose and an explicit internal-only verification override. In isolated mode verify the same HTTP application and bundled assets through container-local requests while real external TCP probes fail; browser tests independently block all nonlocal origins. Cost: normal Compose does not itself enforce egress isolation; air-gapped deployment relies on the host/network boundary. No application runtime Internet calls are introduced. A no-masquerade bridge was tested and rejected because external TCP still succeeded. This is a documented deployment-plan deviation; the approved two-container application architecture is unchanged.

Final review: independent read-only reviewer ran 55 tests and contract checks; no Critical/Important findings, two Minor boundary findings. Regraded both for the final fix pass: valid maximum-length IDs failing the repository contract, and invalid label paths leaving published evidence impede valid registration/retry semantics. Added two regression tests and observed both fail before fixing. Bounded hash-based audit IDs and staged label preparation address the reproductions.

Ruling on declined review scope: ingestion, analytical effectiveness, prioritization, review workflows, production authentication and million-record performance remain outside Phase 1 as explicitly authorized. Cost: none are claimed delivered or validated. The reviewer did not independently repeat ongoing container checks; the report will attribute those checks to the recorded local execution evidence.

Final fixes verified: 57/57 Python tests pass, 5/5 Vitest tests pass, 2/2 browser tests pass after explicit server readiness, contract freshness 20/20, native production build and both Docker image builds pass. A final Windows build with active standalone process failed EBUSY; stopping the process and rerunning fixed the environment condition. A browser startup race was rerun only after actual HTTP readiness.

Task 5: complete — Docker one-command startup and no-pull startup passed; both services healthy. Final isolated-network probes denied external TCP from each container while shell, 8 assets and API status succeeded. Actual stopped-backend UI and immutable dataset/audit preservation across restarts verified. Normal host-port access restored. Full commands and limitations are in docs/phase-1-verification.md.

Finish: preserve local phase-1 branch and workspace, with no push or merge. User explicitly requested stopping after the report rather than proceeding to integration or Phase 2. No deferred review findings remain; documented deployment and crash-recovery limitations remain.
