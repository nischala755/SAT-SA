# SAT-SA Phase 1 verification

Verification date: 2026-09-27. Scope: Phase 1 only. The original problem statement, approved architecture, empty AGENTS.md and approved Phase 1 plan governed implementation. No Phase 2 work was started.

## Final status

Phase 1 is implemented and verified with the documented Docker Desktop networking adjustment below. Final suites: **57 Python tests, 5 frontend unit tests and 2 browser tests passed; no remaining failing tests.** Both native and Docker applications ran successfully. Deterministic data, storage persistence, contract drift detection, actual outage behavior and isolated offline operation were verified. Phase 2 remains unstarted.

The running Compose application is available at `http://127.0.0.1:3001`; native development is also available at `http://127.0.0.1:3000`. The local `phase-1` branch and workspace are preserved; nothing was pushed or merged.

## Delivered files and architecture decisions

- `apps/api/sat_sa_api`: FastAPI application factory, local settings boundary and typed storage health. `/api/v1/health` and `/openapi.json` are real endpoints. No ingestion, analytical, evidence-data or review-action API was added in Phase 1.
- `apps/web`: Next.js/React/TypeScript application shell, same-origin backend status route, visible failure/retry behavior, unit tests and browser smoke tests. No dashboard data, signals or decisions are fabricated.
- `packages/analytics-contracts`: canonical Pydantic models, enums and lifecycle validation. `packages/shared-types/src/generated.ts` and `data/schemas` are reproducible derived contracts.
- `analytics/sat_sa/config`: validated local settings and versioned future analytical configuration. Non-demo mode fails closed because production authentication is not implemented.
- `analytics/sat_sa/repositories`: repository protocols, single-process DuckDB metadata owner, serialized transactions, audit persistence, immutable Parquet writer, bounded entity-filtered reads and composite-reference checks.
- `analytics/sat_sa/synthetic`: seeded generator, scenario definitions and idempotent startup bootstrap. Labels remain in a separate tree and outside evidence table selection.
- Remaining analytics subpackages establish the approved module boundaries only; no analytical engine exists.
- `data/sample/demo`: generated evidence and immutable manifest. `data/ground_truth/demo`: separate labels. `tests`: real domain, configuration, contract, generator, storage and API tests.
- `docker`, Compose files, scripts, dependency locks, README and supporting methodology/deployment documentation make native and container operation repeatable.

The complete file inventory appears in the appendix. `AGENTS.md` remains empty and unchanged. `docs/architecture.md` was not substantively changed during implementation.

Decisions within the approved boundary: DuckDB handles prototype metadata and audit; repository protocols preserve the PostgreSQL migration boundary. Parquet uses an explicit Arrow schema, uncompressed deterministic serialization and pinned PyArrow. The API runs one worker; bootstrap completes before it starts. No background job process is introduced before ingestion/analytics jobs exist. Ajv validates the canonical generated health schema in the frontend server. System fonts and bundled assets avoid runtime resource downloads. PyArrow and pytz support local columnar serialization/timezone conversion; neither adds a service or external runtime API.

## Environment and versions

| Component | Observed version |
| --- | --- |
| Host | Microsoft Windows 11 Pro, 10.0.26200, build 26200 |
| PowerShell | 5.1.26100.9444 |
| Host Python / container Python | 3.12.10 / 3.12.10 |
| Host Node / npm | v24.18.0 / 11.16.0 |
| Container Node / npm | v24.21.0 / 11.19.0 |
| Docker Desktop | 4.80.0 (232116) |
| Docker client / engine | 29.6.1 / 29.6.1; API 1.55 |
| Docker Compose | v5.1.4 |
| Container kernel | 6.18.33.2-microsoft-standard-WSL2; linux/amd64 |
| FastAPI / Pydantic / Uvicorn | 0.141.1 / 2.13.5 / 0.54.0 |
| DuckDB / PyArrow / pytz | 1.5.5 / 23.0.1 / 2026.4 |
| Next.js / React / React DOM | 16.3.6 / 19.3.0 / 19.3.0 |
| TypeScript / Ajv | 7.0.2 / 8.20.0 |
| Pytest / Vitest / Playwright | 9.1.1 / 5.0.2 / 1.63.0 |
| Browser used for smoke tests | Microsoft Edge 154.0.4258.37 |
| Git | 2.54.0.windows.1 |

All Python package versions are in `requirements.lock`; all frontend direct/transitive resolutions are in `apps/web/package-lock.json`. Container base-image resolutions observed during builds: Python `sha256:fd95fa221297a88e1cf49c55ec1828edd7c5a428187e67b5d1805692d11588db`; Node `sha256:0e0ff40c39bc087845bfb27465a0df4ea419520094bc35842ff83dd8cbe6f9b6`. Export prepared application images for an offline deployment rather than rebuilding mutable base tags on the disconnected host.

## Tests and acceptance evidence

| Check | Observed result |
| --- | --- |
| Complete Python suite after review fixes | 57 passed, 0 failed; exit 0 |
| Frontend unit suite | 5 passed, 0 failed; exit 0 |
| Browser smoke suite, after server readiness confirmed | 2 passed, 0 failed; exit 0; external origins blocked and no remote requests observed |
| TypeScript | No type errors; exit 0 |
| Native frontend production build | Passed after stopping the running standalone server; exit 0 |
| Canonical contract freshness | 20 artifacts verified; exit 0 |
| Contract-drift regression | Deliberately altered generated TypeScript causes exporter `--check` to exit 1; restored/repeated generation passes |
| Independent review test pass | 55 passed before the two additional regression tests; no Critical/Important issues initially reported |

The full Python suite covers invalid/naive/reversed timestamps, negative counts/durations, unknown fields, required schema definitions, representable missing evidence, bad configuration and non-demo rejection; transaction rollback, parameterized persistence, immutable duplicate rejection, separate-process reopen, actual storage failures; typed Parquet round trips, allowed evidence tables, bounded paths/pagination and cross-entity references; deterministic artifacts/logical rows, changed seeds, scenario records and separate labels; bootstrap repeatability/corruption detection; API startup, runtime health failure and application restart.

Two independently reviewed boundary findings were reproduced and fixed: valid maximum-length dataset IDs now receive bounded audit identifiers; label output is prepared before evidence publication, preventing invalid label parent paths from leaving an otherwise complete evidence version. Their regression tests failed before the fixes and pass in the final 57-test suite. No validation was relaxed.

An upstream warning remains: Starlette 1.7.0 deprecates its TestClient's `httpx` compatibility path in favor of `httpx2`. It does not fail the tests or affect the application runtime. Playwright also emits a host `NO_COLOR`/`FORCE_COLOR` warning. Neither warning was hidden.

## Deterministic synthetic dataset

Seed: `20260927`; logical dataset version: `demo`; generator/schema version: `1.0.0`; assessment period: `[2025-01-01T00:00:00Z, 2026-01-01T00:00:00Z)`.

| Table | Rows |
| --- | ---: |
| CSEs | 8 |
| Assets | 192 |
| Alerts | 6,816 |
| Cases | 852 |
| Investigation events | 3,322 |
| Escalation records | 2,696 |

Two sectors and peer groups are represented across twelve months. All ten requested scenarios have separate ground-truth labels, including one healthy control. Labels describe injected data, not analytical detections.

Dataset hash: `7501d21aeddf23e29bbb6dd3971ac46798db3274b8863797aa4d502f527f50b8`.

The second explicit CLI generation reproduced all seven evidence artifacts (six Parquet tables plus manifest) and the separate label file byte for byte. Tests also compare logical rows and demonstrate a changed dataset hash for seed `20260928`. Determinism includes the same logical version name and pinned generator/writer versions. The evidence hash observed in the Linux container matched the native Windows generation.

Dataset `created_at` is a fixed synthetic snapshot time; actual registration time is stored separately in the audit. No wall-clock timestamp enters the reproducible dataset artifacts. Existing output directories and duplicate registration are rejected, not overwritten.

## Persistence, runtime, Docker and offline verification

| Runtime check | Observed result |
| --- | --- |
| Native startup | API and standalone web server ready; real HTTP status requests succeed |
| Native frontend → backend | `/api/status` matches the actual API response; one registered dataset; exit 0 |
| Docker builds | Both images built successfully, including after review fixes; exit 0 |
| One-command Compose startup | `docker compose up --build --wait`: exit 0; both services healthy |
| Prepared offline startup | `docker compose up --pull never --no-build --wait`: exit 0; no dependency downloads |
| Container frontend → backend | Web status proxy reports the actual API/storage state; exit 0 |
| Real API outage | API container stopped; proxy returns HTTP 503; browser visibly shows “Backend unavailable” and retry action |
| Process persistence | Independent Python process reopens the registered dataset and its audit entries |
| Application/Compose restart | Dataset manifest and complete audit payloads compare equal before/after restart; exactly one registration audit event remains |
| Isolated runtime | Both services ran on a verified `Internal: true` network; external TCP to `1.1.1.1:443` and `8.8.8.8:443` failed from both containers |
| Application during blocked egress | Frontend HTML, all 8 referenced local assets, and frontend → API health succeeded inside the isolated network |
| Restored normal deployment | Both containers healthy and reachable on localhost ports 3001/8001 |

Exact container subprocess argument vectors, exit codes and outputs are retained in [container-checks.jsonl](verification/container-checks.jsonl); the latest summarized assertions are in [container-results.json](verification/container-results.json). These include the rebuilt-image verification. Evidence for the visible failure is retained in [real-backend-outage.png](verification/real-backend-outage.png), with the healthy shell in [shell.png](verification/shell.png).

The host Internet connection itself was not disabled. The isolated container network removes external routes for the actual runtime checks; browser tests independently block nonlocal requests. This is evidence of offline operation, not a claim that ordinary Compose is an outbound firewall. Image archive transfer/load on a second air-gapped machine was documented but not exercised; image build and no-pull/no-build startup were exercised locally.

## Remaining acceptance gaps

No unresolved functional Phase 1 acceptance failures remain. The original internal-network-plus-host-port packaging assumption was replaced and tested as documented. Physical deployment to another air-gapped host, production identity/security accreditation, encrypted-volume provisioning and scale benchmarks are unverified deployment/future-phase work, not claimed completed. The bootstrap crash window and upstream test warning remain known limitations.

## Deviations and limitations

1. **Deployment-plan adjustment:** Docker Desktop did not publish host ports for the planned internal-only network. The containers were healthy, but `NetworkSettings.Ports` was empty and localhost connections were refused. Normal Compose now uses a standard bridge with loopback-published ports. `compose.offline.yaml` provides the internal-only verification network. This preserves the approved two-container architecture; it changes the implementation plan's networking detail.
2. **Offline operation versus enforcement:** normal Compose does not enforce outbound blocking. Actual isolated checks use the override and verify blocked external TCP alongside successful local application/assets/API access. A controlled deployment must supply its host/network isolation boundary. A no-masquerade bridge was experimentally rejected because it still allowed external TCP; that unsuccessful experiment is not counted as offline proof.
3. **Demo authentication only:** no production authentication, authorization integration, real SOC submission import, analytical calculation or supervisory decision workflow is delivered. Non-demo settings fail closed. No sample passwords or secrets are committed.
4. **Scale:** synthetic generation is bounded and in memory. Entity-filtered evidence reads are paginated in DuckDB, but millions-of-record performance, streaming ingestion and multiwriter operation are not measured or claimed.
5. **Integrity:** hashes detect changed artifacts during bootstrap/verification; they are not digital signatures. Audit persistence is transactional and append-only through repository methods, not tamper-proof against filesystem/database administrators. Encrypted storage is a deployment responsibility.
6. **Crash recovery:** publishing evidence and labels across separate directories cannot be one filesystem transaction. Invalid label destinations are preflighted/staged; a machine crash between final directory publications can still require generation into fresh destinations. Bootstrap refuses incomplete evidence/labels instead of claiming readiness.
7. **Engineering-process adaptation:** approved work was done in the originally empty workspace on local branch `phase-1`; no second worktree was necessary. A checked-in ledger and PowerShell command recorder replaced Bash skill bookkeeping helpers. No remote repository operation occurred.

No architecture-level technology, AI/ML component or major feature was added beyond the approved Phase 1 plan. The local dependency additions support its existing serialization and contract-validation requirements. No LLM, external AI, cloud, SaaS, remote font, CDN resource, telemetry integration or runtime REST adapter was introduced.

## Earlier failures and their disposition

- Docker daemon initially absent: `docker info` exited 1. Starting Docker Desktop enabled subsequent real builds/startup checks.
- First venv test invocation occurred before dependency installation finished: exited 1 because pytest was absent. Not counted as a regression-test RED result.
- Test-first runs failed on missing implementation as expected: models/configuration/export (34), repositories (10), generator (one failure plus five fixture setup errors), health API (3), bootstrap (2), frontend status client (5). These were followed by passing implementations.
- Windows open-lock cleanup and string/Path boundary failed persistence tests; fixed. DuckDB required pytz for timezone-aware Python fetches; dependency explicitly added and locked.
- Browser pre-implementation checks failed because the frontend was absent. A later browser test matched Next.js's route announcer as well as the application alert; the selector was correctly scoped to the main application region and the same failure-message assertion passed.
- Native `next start` warned about standalone output; replaced with the generated standalone-server launcher. A rebuild while that server was active failed with EBUSY; stopping it allowed a successful rebuild. README documents that sequence.
- Initial isolated Compose localhost check failed because internal networking suppressed host-port publication. The documented two-mode verification replaced that unsupported assumption.
- Both review regression tests initially failed, then passed after bounded audit IDs and staged label preparation.
- A final browser run began before the native standalone process was listening, causing one connection-refused failure. After a successful explicit status request established readiness, the complete unchanged browser suite passed 2/2. The failed run is retained in the command history.

## Commands and file inventory

Commands were executed from `C:\Users\keerthish\Desktop\projects\sih3`, using `.venv\Scripts\python` unless stated otherwise. `scripts/Invoke-Check.ps1` records the inner command, its actual exit code and its full local log path. The appendices below enumerate these commands, including failed attempts; container-check JSON additionally preserves each exact argument vector and result.

Initial preparation before the recorder existed: `git init -b phase-1`, `python -m venv .venv`, `docker desktop start` were run sequentially in a command invocation that exited 0. Read-only skill/repository inspection commands are not acceptance checks. File edits were applied directly through patch tooling. Long-running native server commands have readiness evidence rather than a completed exit code while they remain running; terminated development instances are not application-test failures.

<!-- GENERATED_APPENDIX -->

### Recorded commands

Exact completed command invocations, in start-time order. Negative process exits on native server commands reflect deliberate shutdown for rebuilding; see the failure-disposition section. Full machine-readable entries: [commands.jsonl](verification/commands.jsonl). Raw full logs remain at the recorded local artifact paths.

| UTC start | Exact command | Exit code |
| --- | --- | ---: |
| 20260927T112958922 | `.venv\Scripts\python -m pip install -e ".[test]"` | 0 |
| 20260927T113018032 | `docker info` | 0 |
| 20260927T113036828 | `.venv\Scripts\python -m pytest tests/unit/test_models.py tests/unit/test_config.py -q` | 1 |
| 20260927T113043462 | `npm view next version` | 0 |
| 20260927T113123241 | `npm view react version` | 0 |
| 20260927T113140774 | `python --version` | 0 |
| 20260927T113140954 | `node --version` | 0 |
| 20260927T113141022 | `npm --version` | 0 |
| 20260927T113141512 | `docker compose version` | 0 |
| 20260927T113205387 | `python -m pytest tests/unit -q --tb=line` | 1 |
| 20260927T113430848 | `.venv\Scripts\python -m pytest tests/unit -q --tb=short` | 0 |
| 20260927T113437851 | `.venv\Scripts\python scripts/export_contracts.py` | 0 |
| 20260927T113438760 | `.venv\Scripts\python scripts/export_contracts.py --check` | 0 |
| 20260927T113555919 | `.venv\Scripts\python -m pytest tests/integration -q --tb=line` | 1 |
| 20260927T113802899 | `.venv\Scripts\python -m pytest -q --tb=short` | 1 |
| 20260927T113828759 | `.venv\Scripts\python -m pytest -q --tb=short` | 1 |
| 20260927T113853361 | `.venv\Scripts\python -m pip install pytz` | 0 |
| 20260927T113901379 | `.venv\Scripts\python -m pytest -q --tb=short` | 0 |
| 20260927T114019558 | `.venv\Scripts\python -m pytest tests/unit/test_generator.py -q --tb=line` | 1 |
| 20260927T114226580 | `.venv\Scripts\python -m pytest -q --tb=short` | 0 |
| 20260927T114344143 | `.venv\Scripts\python -m pytest tests/integration/test_health.py -q --tb=line` | 1 |
| 20260927T114351047 | `npm --prefix apps/web install --save-exact ajv --no-audit --no-fund` | 0 |
| 20260927T114419452 | `.venv\Scripts\python -m pytest tests/integration/test_bootstrap.py -q --tb=line` | 1 |
| 20260927T114423825 | `.venv\Scripts\python scripts/generate_demo.py --seed 20260927 --output data/sample/demo --labels-output data/ground_truth/demo --register runtime/metadata.duckdb` | 0 |
| 20260927T114513892 | `.venv\Scripts\python -m pytest tests/integration/test_health.py tests/integration/test_bootstrap.py -q --tb=short` | 0 |
| 20260927T114546541 | `.venv\Scripts\python scripts/generate_demo.py --seed 20260927 --output artifacts/replica/demo --labels-output artifacts/replica-labels/demo` | 0 |
| 20260927T114547347 | `.venv\Scripts\python -m pip freeze --exclude-editable` | 0 |
| 20260927T114708500 | `.venv\Scripts\python -m pip freeze --exclude-editable > requirements.lock` | 0 |
| 20260927T114711779 | `git status --short` | 0 |
| 20260927T114733194 | `.venv\Scripts\python -m uvicorn sat_sa_api.main:create_app --factory --host 127.0.0.1 --port 8000` | -1 |
| 20260927T114908656 | `.venv\Scripts\python scripts/verify_phase1.py` | 0 |
| 20260927T114913679 | `docker compose config --quiet` | 0 |
| 20260927T114917918 | `npm --prefix apps/web install --save-dev --save-exact typescript @types/node @types/react @types/react-dom vitest @playwright/test --no-audit --no-fund` | 0 |
| 20260927T114924864 | `docker compose build api` | 0 |
| 20260927T115142100 | `npm --prefix apps/web test` | 1 |
| 20260927T115203322 | `npm --prefix apps/web run test:e2e` | 1 |
| 20260927T115222674 | `docker compose up api --pull never --no-build --wait` | 0 |
| 20260927T115425266 | `npm --prefix apps/web test` | 0 |
| 20260927T115430928 | `npm --prefix apps/web run typecheck` | 0 |
| 20260927T115433874 | `npm --prefix apps/web run build` | 0 |
| 20260927T115442393 | `docker compose build web` | 0 |
| 20260927T115556700 | `.venv\Scripts\python -m pytest -q --tb=short` | 0 |
| 20260927T115808243 | `.venv\Scripts\python scripts/export_contracts.py --check` | 0 |
| 20260927T115812780 | `npm --prefix apps/web start` | -1 |
| 20260927T115823138 | `.venv\Scripts\python scripts/verify_phase1.py --web-url http://127.0.0.1:3000` | 0 |
| 20260927T115824764 | `npm --prefix apps/web run test:e2e` | 1 |
| 20260927T115955579 | `npm --prefix apps/web start` | -1 |
| 20260927T120005406 | `docker compose up --pull never --no-build --wait` | 0 |
| 20260927T120020899 | `npm --prefix apps/web run test:e2e` | 0 |
| 20260927T120032946 | `git add AGENTS.md docs/architecture.md docs/problem-statement.md docs/superpowers/plans/2026-09-27-phase-1.md` | 0 |
| 20260927T120040049 | `git commit -m "docs: record approved SAT-SA Phase 1 scope"` | 0 |
| 20260927T120040628 | `git add .` | 0 |
| 20260927T120044435 | `git diff --cached --stat` | 0 |
| 20260927T120120747 | `.venv\Scripts\python scripts/verify_containers.py` | 1 |
| 20260927T120133059 | `docker compose ps` | 0 |
| 20260927T120136910 | `docker compose logs --tail 15 web` | 0 |
| 20260927T120140515 | `docker compose port web 3000` | 0 |
| 20260927T120141177 | `curl.exe --max-time 5 -v http://127.0.0.1:3001/api/status` | 7 |
| 20260927T120153438 | `docker inspect sat-sa-web-1 --format "{{json .HostConfig.PortBindings}} {{json .NetworkSettings.Ports}}"` | 0 |
| 20260927T120157526 | `docker network inspect sat-sa_offline` | 0 |
| 20260927T120226725 | `docker network create --driver bridge --opt com.docker.network.bridge.enable_ip_masquerade=false sat-sa-probe` | 0 |
| 20260927T120228171 | `docker run --rm --network sat-sa-probe --entrypoint python sat-sa-api:phase1 -c "import socket; socket.create_connection(('1.1.1.1',443),timeout=3)"` | 0 |
| 20260927T120324800 | `docker compose up --pull never --no-build --wait` | 0 |
| 20260927T120342449 | `docker network rm sat-sa-probe` | 0 |
| 20260927T120445759 | `.venv\Scripts\python scripts/verify_containers.py` | 0 |
| 20260927T120541222 | `.venv\Scripts\python -m pytest tests/integration/test_repository.py::test_maximum_length_dataset_identifier_can_be_registered tests/unit/test_generator.py::test_invalid_label_destination_does_not_publish_evidence -q --tb=short` | 1 |
| 20260927T120626757 | `.venv\Scripts\python -m pytest -q --tb=short` | 0 |
| 20260927T120702250 | `.venv\Scripts\python scripts/export_contracts.py --check` | 0 |
| 20260927T120704249 | `docker compose build` | 0 |
| 20260927T120714081 | `npm --prefix apps/web test` | 0 |
| 20260927T120717938 | `npm --prefix apps/web run typecheck` | 0 |
| 20260927T120720345 | `npm --prefix apps/web run build` | 1 |
| 20260927T120753022 | `docker version --format json` | 0 |
| 20260927T120753815 | `npm --prefix apps/web ls --depth=0` | 0 |
| 20260927T120801501 | `.venv\Scripts\python -m pip list --format=json` | 0 |
| 20260927T120804149 | `git diff --check` | 0 |
| 20260927T120804615 | `git diff --cached --check` | 0 |
| 20260927T120910564 | `docker compose config --quiet` | 0 |
| 20260927T120915889 | `docker compose -f compose.yaml -f compose.offline.yaml config --quiet` | 0 |
| 20260927T120958091 | `npm --prefix apps/web run build` | 0 |
| 20260927T120958904 | `docker compose up --pull never --no-build --wait` | 0 |
| 20260927T121053558 | `docker compose exec -T api python --version` | 0 |
| 20260927T121056185 | `docker compose exec -T web node --version` | 0 |
| 20260927T121057910 | `docker compose exec -T web npm --version` | 0 |
| 20260927T121128681 | `.venv\Scripts\python scripts/verify_containers.py` | 0 |
| 20260927T121139378 | `npm --prefix apps/web run test:e2e` | 1 |
| 20260927T121600789 | `curl.exe --fail --max-time 10 http://127.0.0.1:3000/api/status` | 0 |
| 20260927T121620714 | `.venv\Scripts\python scripts/verify_phase1.py --web-url http://127.0.0.1:3000` | 0 |
| 20260927T121623596 | `npm --prefix apps/web run test:e2e` | 0 |
| 20260927T121648963 | `docker compose up --build --wait` | 0 |
| 20260927T121803502 | `git --version` | 0 |
| 20260927T121804878 | `git rev-parse --git-dir --git-common-dir --show-toplevel` | 0 |
| 20260927T121806587 | `git branch --show-current` | 0 |
| 20260927T121821199 | `.venv\Scripts\python scripts/verify_phase1.py --api-url http://127.0.0.1:8001 --web-url http://127.0.0.1:3001` | 0 |
| 20260927T121822679 | `docker compose ps` | 0 |
| 20260927T121941137 | `git diff --check` | 0 |
| 20260927T121941921 | `git add .` | 0 |
| 20260927T121948001 | `git diff --cached --check` | 0 |

Current long-running native commands (readiness and HTTP verified; no terminal exit code yet):

```powershell
.venv\Scripts\python -m uvicorn sat_sa_api.main:create_app --factory --host 127.0.0.1 --port 8000 --workers 1
npm --prefix apps/web start
```

Development process maintenance used `Stop-Process -Id 27852` for the initial Next server, then `Stop-Process -Id 26136` and `Stop-Process -Id 24356` before the final Windows rebuild/API restart. Only processes started for this task were stopped. Dependency-lock capture used `.venv\Scripts\python -m pip freeze --exclude-editable`, with UTF-8 output normalized before Docker builds. Package metadata was edited to enable ESM and the standalone startup script. These setup/bookkeeping edits were not substitute acceptance checks.

### Complete created/modified file inventory

Relative to the initially empty application workspace (the approved architecture and plan pre-existed; the plan completion checkboxes were updated). Generated schemas and synthetic artifacts are included. Ignored runtime databases, dependencies, build outputs and raw local logs are excluded.

```text
.dockerignore
.gitattributes
.gitignore
AGENTS.md
README.md
analytics/sat_sa/__init__.py
analytics/sat_sa/config/__init__.py
analytics/sat_sa/config/settings.py
analytics/sat_sa/ingestion/__init__.py
analytics/sat_sa/negative_space/__init__.py
analytics/sat_sa/normalization/__init__.py
analytics/sat_sa/peer_analysis/__init__.py
analytics/sat_sa/prioritization/__init__.py
analytics/sat_sa/repositories/__init__.py
analytics/sat_sa/repositories/duckdb_metadata.py
analytics/sat_sa/repositories/interfaces.py
analytics/sat_sa/repositories/parquet_evidence.py
analytics/sat_sa/repositories/relationships.py
analytics/sat_sa/risk/__init__.py
analytics/sat_sa/signals/__init__.py
analytics/sat_sa/synthetic/__init__.py
analytics/sat_sa/synthetic/bootstrap.py
analytics/sat_sa/synthetic/generator.py
analytics/sat_sa/synthetic/scenarios.py
analytics/sat_sa/validation/__init__.py
apps/api/sat_sa_api/__init__.py
apps/api/sat_sa_api/main.py
apps/api/sat_sa_api/schemas.py
apps/api/sat_sa_api/settings.py
apps/web/app/api/status/route.ts
apps/web/app/globals.css
apps/web/app/layout.tsx
apps/web/app/page.tsx
apps/web/lib/status.test.ts
apps/web/lib/status.ts
apps/web/next-env.d.ts
apps/web/next.config.ts
apps/web/package-lock.json
apps/web/package.json
apps/web/playwright.config.ts
apps/web/scripts/next.mjs
apps/web/scripts/start.mjs
apps/web/tests/shell.spec.ts
apps/web/tsconfig.json
apps/web/vitest.config.ts
compose.offline.yaml
compose.yaml
config/defaults.json
data/ground_truth/demo/labels.json
data/sample/demo/alerts.parquet
data/sample/demo/assets.parquet
data/sample/demo/cases.parquet
data/sample/demo/cses.parquet
data/sample/demo/escalations.parquet
data/sample/demo/investigation_events.parquet
data/sample/demo/manifest.json
data/schemas/Alert.json
data/schemas/AnalyticsRun.json
data/schemas/Artifact.json
data/schemas/AssessmentPeriod.json
data/schemas/Asset.json
data/schemas/AuditEvent.json
data/schemas/CSE.json
data/schemas/Case.json
data/schemas/Contract.json
data/schemas/DatasetManifest.json
data/schemas/DatasetVersion.json
data/schemas/EntityRecord.json
data/schemas/EscalationRecord.json
data/schemas/EvidenceReference.json
data/schemas/HealthStatus.json
data/schemas/InvestigationEvent.json
data/schemas/Provenance.json
data/schemas/ReviewDecision.json
data/schemas/SupervisorySignal.json
docker/api.Dockerfile
docker/web.Dockerfile
docs/analytics-methodology.md
docs/architecture.md
docs/data-dictionary.md
docs/deployment.md
docs/phase-1-ledger.md
docs/phase-1-verification.md
docs/problem-statement.md
docs/superpowers/plans/2026-09-27-phase-1.md
docs/validation-methodology.md
docs/verification/commands.jsonl
docs/verification/container-checks.jsonl
docs/verification/container-results.json
docs/verification/files.txt
docs/verification/real-backend-outage.png
docs/verification/shell.png
packages/analytics-contracts/sat_sa_contracts/__init__.py
packages/analytics-contracts/sat_sa_contracts/enums.py
packages/analytics-contracts/sat_sa_contracts/models.py
packages/shared-types/src/generated.ts
pyproject.toml
requirements.lock
scripts/Invoke-Check.ps1
scripts/check_outage.mjs
scripts/export_contracts.py
scripts/generate_demo.py
scripts/verify_containers.py
scripts/verify_phase1.py
tests/__init__.py
tests/fixtures/__init__.py
tests/fixtures/evidence.py
tests/integration/test_bootstrap.py
tests/integration/test_health.py
tests/integration/test_parquet.py
tests/integration/test_repository.py
tests/unit/test_config.py
tests/unit/test_contract_export.py
tests/unit/test_generator.py
tests/unit/test_models.py
```

### Handoff boundary

Phase 1 only. Preserve this workspace and local branch for user review. Do not begin Phase 2 without explicit approval of this report.
