# SAT-SA

**VISTA repository · Local supervisory analytics prototype**

[Quick start](#quick-start) · [Setup](#native-setup-windows-powershell) · [Architecture](#architecture-and-repository-map) · [Data](#synthetic-dataset) · [Qwen](#optional-local-qwen) · [Tests](#tests-and-verification) · [Troubleshooting](#troubleshooting) · [Documentation](#documentation-map)

<details>
<summary><strong>Choose your starting point</strong></summary>

- Run the synthetic demonstration: follow the Docker quick start.
- Develop locally: follow the Python/Node setup below.
- Examine evidence: read the data dictionary and sample Parquet files.
- Audit the implementation: read the Phase 1 verification report.
- Deploy without Internet: prepare images first, then follow the air-gap instructions.

This README uses GitHub-native collapsible guides, navigation links and Mermaid diagrams. It does not require executable JavaScript or a documentation service.

</details>

## Quick start

Prerequisites: Git, Docker with Compose, and access to dependency registries for the initial build, or prepared application images.

```powershell
git clone https://github.com/nischala755/VISTA.git
cd VISTA
docker compose up --build --wait
```

Open **http://127.0.0.1:3001**. Expect **Backend connected**, storage ready, and **1** registered dataset. First startup generates synthetic evidence; subsequent startups verify and reuse it.

| Service | Docker | Native |
| --- | --- | --- |
| Application | http://127.0.0.1:3001 | http://127.0.0.1:3000 |
| Backend health | http://127.0.0.1:8001/api/v1/health | http://127.0.0.1:8000/api/v1/health |
| OpenAPI schema | http://127.0.0.1:8001/openapi.json | http://127.0.0.1:8000/openapi.json |
| Frontend status proxy | http://127.0.0.1:3001/api/status | http://127.0.0.1:3000/api/status |

<details>
<summary><strong>Container operations and persistence</strong></summary>

```powershell
docker compose ps
docker compose logs --tail 100 api web
docker compose stop
docker compose start --wait
```

`docker compose down` retains the named data volume. Do not add `--volumes` when preserving evidence and audit history. `sat-sa_sat-sa-data` is mounted at `/var/lib/sat-sa` inside the API container. Bootstrap finishes before the API starts; one API worker owns metadata writes.

</details>

<details>
<summary><strong>View the verified application and failure state</strong></summary>

![Actual Phase 1 application shell](docs/verification/shell.png)

![Actual backend outage with visible retry](docs/verification/real-backend-outage.png)

These screenshots record the verification session; they are not live status indicators. The second was captured with the backend actually stopped.

</details>

## Delivery status

| Capability | Status |
| --- | --- |
| Application shell and actual storage/backend health | Implemented |
| Domain validation and reproducible generated contracts | Implemented |
| Immutable Parquet evidence and DuckDB metadata/audit | Implemented |
| Seeded multi-entity synthetic dataset | Implemented |
| Separate ground truth | Implemented; excluded from evidence table selection |
| Docker and isolated core runtime verification | Verified with networking limits documented below |
| Ingestion UI, analytics, evidence-gap detection and ranking | Implemented |
| Assessment views, human reviews, audit and configured bearer identities | Implemented; hardening limits apply |
| Optional evidence-summary CLI | Qwen verified locally; Mistral adapter implemented, live request returned HTTP 429 |

Supervisory Analytics Tool for SOC Assessment

SAT-SA is intended to help NCIIPC supervisors examine periodic submitted SOC evidence. The product chain is submitted evidence → normalization → supervisory analytics → evidence gaps/anomalies → review prioritization → human examination → auditable supervisory decision.

**Current scope:** CSV/JSON ingestion, deterministic indicators across eight signal families, explicit evidence gaps, peer/history comparisons, review prioritization, human decisions, validation and audit. Results are computed from evidence. The Phase 1 report is historical; see the [completion report](docs/completion-verification.md) for current verification and limitations.

## Requirements and architecture

Authority: [problem statement](docs/problem-statement.md), [approved architecture](docs/architecture.md), [AGENTS.md](AGENTS.md), then the [completion plan](docs/superpowers/plans/2026-09-27-completion.md). Root AGENTS.md remains empty; Next.js generated frontend guidance is scoped to `apps/web/AGENTS.md`.

Next.js/TypeScript serves the application shell and a same-origin status proxy. FastAPI/Pydantic owns the status API. Repository interfaces separate local DuckDB metadata from immutable Parquet evidence. Python analytical modules implement versioned, explainable rules independently of the UI and optional AI. One process owns metadata writes; stop the API before running a metadata-writing CLI.

## Native setup (Windows PowerShell)

Use Python 3.12 and Node.js 24. Dependency installation requires a prepared package cache or a network connection. Runtime uses only local services.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.lock
.venv\Scripts\python -m pip install -e . --no-deps
npm --prefix apps/web ci --no-audit --no-fund
.venv\Scripts\python scripts/export_contracts.py --check
```

Initialize a local demo volume before starting the API:

```powershell
.venv\Scripts\python -m sat_sa.synthetic.bootstrap
```

This generates evidence in `runtime/evidence/demo`, separate labels in `runtime/ground_truth/demo` and metadata in `runtime/metadata.duckdb`. It is idempotent: subsequent calls verify existing evidence and preserve registration/audit history. A changed seed, corrupt artifact or conflicting immutable registration fails explicitly. Do not run it concurrently with the API.

Terminal 1, from the repository root:

```powershell
.venv\Scripts\python -m uvicorn sat_sa_api.main:create_app --factory --host 127.0.0.1 --port 8000 --workers 1
```

Terminal 2:

```powershell
npm --prefix apps/web run dev
```

Open `http://127.0.0.1:3000`. The shell shows actual API connectivity and registered dataset count. Its retry action reports backend failures visibly. API health: `http://127.0.0.1:8000/api/v1/health`; OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`. CDN-backed interactive documentation is disabled.

For a production frontend build:

Stop any running production frontend before rebuilding, particularly on Windows where the running standalone server holds its build directory open.

```powershell
npm --prefix apps/web run build
npm --prefix apps/web start
```

Linux/macOS use `.venv/bin/python` in place of `.venv\Scripts\python`; the other commands are equivalent.

## Synthetic dataset

Checked-in evidence: `data/sample/demo`; ground truth: `data/ground_truth/demo`. Seed `20260927` produces eight entities, two sectors/cohorts, twelve months in 2025, 192 assets, 6,816 alerts, 852 cases, 3,322 investigation events and 2,696 escalation records. All names and evidence are synthetic. Investigation text is represented by short synthetic actions and notes lengths, not sensitive raw notes.

Generate another copy into unused directories:

```powershell
.venv\Scripts\python scripts/generate_demo.py --seed 20260927 --output artifacts/replica/demo --labels-output artifacts/replica-labels/demo
```

Paths must not already exist. The dataset folder name is its logical version ID; use `demo` in both copies when comparing full manifest bytes. The same seed, version ID and pinned writer version produce equal logical records and artifact hashes. A different seed changes evidence. The generator never reads labels. Labels are not an allowed evidence repository table and have no API route.

To register a newly generated version in an inactive local database, append `--register runtime/metadata.duckdb`. Duplicate registration is an error, including identical duplicates; bootstrap provides explicit idempotence without overwriting a version.

## Tests and verification

```powershell
.venv\Scripts\python -m pytest -q
.venv\Scripts\python scripts/export_contracts.py --check
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
```

With the API and web application running and the replica generated:

```powershell
.venv\Scripts\python scripts/verify_phase1.py --web-url http://127.0.0.1:3000
npm --prefix apps/web run test:e2e
```

Browser tests default to locally installed Microsoft Edge. For another prepared Playwright browser, set `PLAYWRIGHT_CHANNEL=chromium` and install its browser binary during dependency preparation, not at offline runtime. Set `SAT_SA_WEB_URL` to test a different application address.

The [verification report](docs/phase-1-verification.md) contains actual command results and acceptance gaps. Synthetic benchmark metrics are reported separately from manual-review outcomes and do not establish real-world effectiveness.

## Docker and air-gapped deployment

On a machine with Docker running and access to build dependencies:

```powershell
docker compose up --build --wait
```

Open `http://127.0.0.1:3001`; API health is on `http://127.0.0.1:8001/api/v1/health`. Ports differ from native development so both can be verified independently. A local bridge provides loopback-published ports, and the named `sat-sa_sat-sa-data` volume preserves evidence and metadata. Images generate the demo on first start; no runtime download is required. Normal Compose does not itself enforce outbound network blocking; the air-gapped host/network supplies that boundary.

Prepare and transfer images before disconnecting:

```powershell
docker compose build
docker image save -o sat-sa-phase1-images.tar sat-sa-api:phase1 sat-sa-web:phase1
```

On the air-gapped host, copy the image archive and `compose.yaml`, then:

```powershell
docker image load -i sat-sa-phase1-images.tar
docker compose up --pull never --no-build --wait
```

See [deployment details](docs/deployment.md) for storage, boundaries and verification. Building on an unprepared disconnected host is not supported.

`python scripts/verify_containers.py` verifies actual outage handling and persistence, then temporarily applies `compose.offline.yaml`. That override puts both services on an internal-only network, verifies denied external TCP access and successful internal frontend/assets/API requests, and restores normal localhost access. Docker Desktop does not publish host ports in the isolated mode. The script must run only against this project's synthetic demo; it stops/recreates its services and preserves the volume.

## Configuration and limits

`SAT_SA_STORAGE_ROOT` selects local storage; `SAT_SA_DEMO_SEED` selects the deterministic seed before initial generation. `SAT_SA_DEMO_MODE=false` requires configured `SAT_SA_AUTH_TOKENS`; missing authentication configuration fails closed. No login credentials are required for the local synthetic demonstration. This prototype is not security-accredited for restricted submissions. Keep the demonstration on a controlled host.

`config/defaults.json` contains documented future analytical configuration. Active rules use validated `config/engine.json`; `config/defaults.json` retains the original foundation configuration. See [data dictionary](docs/data-dictionary.md), [methodology boundaries](docs/analytics-methodology.md) and [validation methodology](docs/validation-methodology.md).

The synthetic generator builds a bounded demonstration dataset in memory. This is not a tested million-record importer. The evidence reader applies entity filters and pagination in DuckDB; later ingestion needs streaming/chunking. Filesystem administrators can modify local files; hashes detect altered artifacts during verification/bootstrap but are not cryptographic signing or tamper-proof audit storage. Encryption at rest is a deployment-managed encrypted-volume responsibility.

## Architecture and repository map

```mermaid
flowchart LR
    Browser[Local browser] --> Web[Next.js / TypeScript]
    Web -->|Status proxy| API[FastAPI / Pydantic]
    API --> Repo[Repository interfaces]
    Repo --> DB[(DuckDB metadata and audit)]
    Repo --> Evidence[(Immutable Parquet evidence)]
    Generator[Seeded generator] --> Evidence
    Generator --> Labels[(Separate ground truth)]
    Contracts[Pydantic contracts] --> API
    Contracts --> Types[Generated schemas and TypeScript]
    Types --> Web
```

The supervisory reasoning chain is:

```mermaid
flowchart TD
    A[Submitted SOC evidence] --> B[Normalization]
    B --> C[Supervisory analytics]
    C --> D[Evidence gaps and anomalies]
    D --> E[Review prioritization]
    E --> F[Human examination]
    F --> G[Auditable supervisory decision]
```

```text
apps/api/sat_sa_api/          FastAPI factory and storage health
apps/web/                    Next.js shell, status proxy and tests
analytics/sat_sa/config/     Validated settings
analytics/sat_sa/repositories/ DuckDB/Parquet repository implementations
analytics/sat_sa/synthetic/  Seeded generator and bootstrap
analytics/sat_sa/...         Reserved analytics and ingestion boundaries
packages/analytics-contracts/ Canonical Pydantic domain models
packages/shared-types/      Generated TypeScript contracts
data/sample/demo/           Six evidence tables and immutable manifest
data/ground_truth/demo/      Separate synthetic scenario labels
data/schemas/               Generated JSON schemas
config/                     Active engine thresholds and foundation configuration
docker/                     API/frontend Dockerfiles
scripts/                    Generation and verification commands
tests/                      Python regression tests
docs/                       Architecture, methods and verification
compose.yaml                Local deployment
compose.offline.yaml        Internal-network verification override
```

### Domain and evidence rules

| Contract | Responsibility |
| --- | --- |
| CSE | Entity, sector, cohort, criticality and assessment period |
| Asset | Entity-scoped inventory and monitoring expectation |
| Alert | Lifecycle and links to assets/cases/escalation evidence |
| Case | Investigation lifecycle, assignment and disposition |
| InvestigationEvent | Timestamped action and source provenance |
| EscalationRecord | Explicit escalation linked to an alert/case |
| DatasetVersion | Immutable hashes, counts and schema/generator versions |
| AnalyticsRun | Persisted execution provenance, configuration and hashes |
| SupervisorySignal | Calculated evidence-backed review indicator |
| EvidenceReference | Dataset/entity/type/record identity and provenance |
| ReviewDecision | Human-authored decision; never generated by analytics |
| AuditEvent | Persisted registration/action history |

Unknown fields, naive timestamps, reversed lifecycles and invalid negative counts fail validation. Missing optional evidence remains null. Entity-scoped references cannot be satisfied by an identically named record in another CSE. Missing escalation evidence is not proof that escalation never occurred.

## Runtime configuration reference

| Variable | Default | Purpose |
| --- | --- | --- |
| `SAT_SA_STORAGE_ROOT` | `runtime` | Local data root; Compose uses `/var/lib/sat-sa` |
| `SAT_SA_DEMO_MODE` | `true` | Non-demo requires configured bearer identities |
| `SAT_SA_AUTH_TOKENS` | `{}` | JSON map from secret tokens to server-owned actor/role |
| `SAT_SA_DEMO_ROLE` | `examiner` | Server-owned demo role |
| `SAT_SA_INTERNAL_EXPORT_URL` | Unset | Configured private-IP export; disabled by default |
| `SAT_SA_DEMO_SEED` | `20260927` | First-generation seed; cannot overwrite existing evidence |
| `SAT_SA_API_URL` | `http://127.0.0.1:8000` | Frontend's server-side API URL; Compose uses `http://api:8000` |
| `NEXT_TELEMETRY_DISABLED` | Set by launch scripts | Disables Next.js telemetry |
| `SAT_SA_CONFIG` | `config/defaults.json` | Future analytical configuration; inactive in this phase |
| `SAT_SA_WEB_URL` | Native local application | Browser-test target |
| `PLAYWRIGHT_CHANNEL` | `msedge` | Prepared browser for tests |

Set variables in the process's launching shell. The backend does not automatically load `.env`. Compose only passes variables explicitly referenced by its configuration. No API key is required; never put credentials in tracked files.

<details>
<summary><strong>Linux/macOS native setup</strong></summary>

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install -e . --no-deps
npm --prefix apps/web ci --no-audit --no-fund
.venv/bin/python scripts/export_contracts.py --check
.venv/bin/python -m sat_sa.synthetic.bootstrap
.venv/bin/python -m uvicorn sat_sa_api.main:create_app --factory --host 127.0.0.1 --port 8000 --workers 1
```

In another terminal at the repository root, run `npm --prefix apps/web run dev`. These are equivalent setup instructions; the recorded native verification used Windows. Linux runtime was tested in Docker, not every Linux/macOS host configuration.

</details>

## Optional local Qwen and Mistral summaries

AI is an optional **command-line drafting aid**, separate from analytics and decisions. It selects at most 10 records from one immutable dataset/CSE, verifies artifacts and includes source records/references and input/dataset hashes. Drafts are untrusted text requiring human review. Labels are never included. No automatic fallback or model download occurs.

<details>
<summary><strong>Local Qwen through Ollama</strong></summary>

The tested host uses Ollama `0.34.4` with `qwen3.5:2b` already installed. Prepare dependencies before disconnecting:

```powershell
ollama list
# Preparation only, when the model is absent:
ollama pull qwen3.5:2b
```

For a dedicated service, or configure/restart the existing desktop service with these settings:

```powershell
$env:OLLAMA_NO_CLOUD = '1'
$env:OLLAMA_HOST = '127.0.0.1:11434'
ollama serve
```

From the repository root:

```powershell
.venv\Scripts\python scripts/summarize_evidence.py --cse CSE-01 --table alerts --limit 3
```

The adapter uses loopback only, disables proxies/redirects, and bounds context, output and timeout. A real local generation succeeded. **Qwen inference with enforced host egress denial has not been verified**; core container offline verification is separate. Model disk size is not a RAM requirement.

</details>

<details>
<summary><strong>Mistral — explicit optional Internet exception</strong></summary>

Mistral is disabled unless selected with `--provider mistral --allow-cloud`. This sends the selected evidence to Mistral. It never generates analytical signals, priorities or decisions. Use only synthetic or explicitly approved evidence.

Configure a valid key in the invoking shell without putting its value in command history:

```powershell
$credential = Get-Credential -UserName 'mistral' -Message 'Enter API key in password field'
$env:MISTRAL_API_KEY = $credential.GetNetworkCredential().Password
$env:SAT_SA_MISTRAL_MODEL = 'mistral-small-latest'
.venv\Scripts\python scripts/summarize_evidence.py --cse CSE-01 --limit 1 --provider mistral --allow-cloud
Remove-Item Env:MISTRAL_API_KEY
```

The supplied key was used transiently for verification and was not stored in the repository. The provider returned **HTTP 429**; successful live Mistral generation remains unverified. Resolve quota/rate limits before retrying. Rotate any key exposed in chat. `.env.example` contains names only; scripts do not automatically load it.

</details>

Sources: [Ollama chat API](https://docs.ollama.com/api/chat), [Ollama server configuration](https://docs.ollama.com/faq), [Mistral chat API](https://docs.mistral.ai/api/endpoint/chat). See the summary design and architecture addendum for the authorized exception.

## Recorded verification results

The [Phase 1 report](docs/phase-1-verification.md) records exact commands, versions, failures encountered and final results on **2026-09-27**. These are historical results, not live badges.

| Gate | Result |
| --- | --- |
| Python suite | 57 passed |
| Frontend unit suite | 5 passed |
| Browser suite | 2 passed |
| Type checking and production build | Passed |
| Contract freshness | 20 artifacts verified |
| Same-seed records and artifact hashes | Identical; Windows/Linux hash matched |
| Different seed | Different dataset |
| Duplicate registration / immutable version | Overwrite rejected |
| Process/application/container restart | Metadata and audit persisted |
| Actual backend outage | Visible failure and retry |
| Docker build and startup | Verified |
| Core isolated runtime | Verified with denied external TCP probes |
| Qwen inference / AI offline isolation | Not yet verified |

Regenerate contracts only after an intentional canonical model change:

```powershell
.venv\Scripts\python scripts/export_contracts.py
.venv\Scripts\python scripts/export_contracts.py --check
```

Commit canonical and generated changes together. Do not hand-edit generated files or weaken validation to resolve drift. Dataset determinism does not imply future generated prose will be deterministic across model versions or hardware.

## Troubleshooting

<details>
<summary><strong>Backend unavailable</strong></summary>

Check the API health URL directly. Confirm storage is usable and `SAT_SA_API_URL` is correct from the frontend process's network. Within Compose, `127.0.0.1` means the web container itself; use the configured `http://api:8000`. Inspect service logs, then retry. A rendered page alone does not establish backend connectivity.

</details>

<details>
<summary><strong>DuckDB lock or competing writer</strong></summary>

Run one API worker. Stop it before any CLI writes to the same metadata database, then restart it. Repository locks serialize one process's writes; they do not turn DuckDB into a multi-process database server. PostgreSQL remains a future repository migration boundary.

</details>

<details>
<summary><strong>Dataset destination already exists</strong></summary>

Generation intentionally refuses existing destinations. Select an unused parent directory; retain the same final folder name when comparing manifest bytes. Bootstrap is idempotent for existing demo storage. Use a new storage location for a different seed instead of replacing evidence.

</details>

<details>
<summary><strong>Windows build reports EBUSY</strong></summary>

Stop the production frontend holding its standalone directory open, build, then restart. Do not kill unrelated Node processes. This condition and its resolution are recorded in the verification report.

</details>

<details>
<summary><strong>Isolated Docker services are healthy but host ports do not respond</strong></summary>

The tested Docker Desktop internal-only network prevented host-published access. The verifier probes HTML, assets and API from inside that network, then restores normal Compose. Normal Compose supports host access but is not an outbound firewall; the deployment host/network must supply isolation.

</details>

<details>
<summary><strong>Browser tests cannot find a browser</strong></summary>

Tests default to installed Microsoft Edge. Prepare a supported browser before disconnecting and select it with `PLAYWRIGHT_CHANNEL`. Browser download is a testing dependency preparation operation, not an application runtime requirement.

</details>

## Documentation map

| Document | Purpose |
| --- | --- |
| [Problem statement](docs/problem-statement.md) | Authoritative functional requirements |
| [Architecture](docs/architecture.md) | Approved boundaries and future system |
| [AGENTS.md](AGENTS.md) | Engineering instructions; currently empty |
| [Phase 1 plan](docs/superpowers/plans/2026-09-27-phase-1.md) | Approved implementation sequence |
| [Verification report](docs/phase-1-verification.md) | Commands, results, deviations and acceptance evidence |
| [Data dictionary](docs/data-dictionary.md) | Fields, units and missingness |
| [Analytics methodology](docs/analytics-methodology.md) | Analytical boundaries |
| [Validation methodology](docs/validation-methodology.md) | Evaluation approach and limits |
| [Deployment](docs/deployment.md) | Local storage and offline deployment |
| [Qwen design](docs/local-qwen-design.md) | Proposed summary extension |

## Contribution and scope

Keep changes traceable to the requirements and architecture. Preserve entity-scoped references, immutability, missingness, label separation and generated-contract freshness. Add meaningful regression tests for behavior changes and report architectural deviations explicitly.

The user authorized phases 2–10 after Phase 1. See the completion report for implemented workflows, tested boundaries and limitations. Use synthetic data on a controlled local host. No software license has been added; public repository visibility alone does not grant a license.


## Demonstrate the supervisory workflow

1. Start Compose. The first demo startup computes a real analytical run in the background.
2. Select an assessment run to keep its immutable dataset, configuration and period in context.
3. Open **CSE-01**, inspect **High-severity alerts closed unusually quickly**, then open a source record.
4. Compare observations, calculation, peer/history context and the supervisory hypothesis separately.
5. Open **Negative space** for expected/observed/gap evidence. Alert absence does not prove monitoring failure.
6. Open **Review queue** for deduplicated samples and additive priority contributions.
7. Record a human outcome and note. **Audit trail** records actor, time and run. Confirmed concern is a human action only.
8. Open **Validation** for benchmark denominators and separate human-review outcomes.
9. Use **Data ingestion** to upload exports, map columns, preview validation and publish an immutable version. Select it and run analytics.

### Authentication boundary

Default demo identity is `local-demo-examiner`; no password is needed for synthetic local use. Roles are enforced on the API; browser-supplied role/actor fields are rejected. For non-demo operation set `SAT_SA_DEMO_MODE=false` and `SAT_SA_AUTH_TOKENS` to a locally supplied JSON map of secret tokens to `{ "actor": "name", "role": "reader|examiner|administrator" }`. The frontend keeps entered tokens in page memory only. This is a prototype boundary, not SSO, MFA or security accreditation. Use deployment-managed TLS/access controls beyond loopback.

### Database and internal REST exports

Database exports use the CSV/JSON contracts. `POST /api/v1/ingestion/internal` requires an administrator and configured `SAT_SA_INTERNAL_EXPORT_URL` with a literal private IP. Redirects, proxies, public hostnames and link-local metadata endpoints are rejected. The source must return `{ "files": [...] }` using the submission contract. It is disabled by default and accepts no caller-supplied URL.

### Prototype limits

- Uploads: 2 MB per file, 12 files, 10,000 rows; all-or-nothing validation.
- Analytics: at most 100,000 input records. The bounded in-memory orchestrator is **not million-record readiness**. Larger workloads require streaming/SQL aggregation and measured benchmarks.
- Metadata: one process/worker; no distributed job service or PostgreSQL implementation.
- Drafts are not certified as complete, factually correct or deterministic. Model text cannot automatically become a signal or decision.
- Filesystem administrators can change local files. Hashes detect changed artifacts; storage is not signed or tamper-proof.
- Raw imports, evidence and registration span filesystem/database boundaries. A crash may leave raw files or an unregistered immutable directory; neither is silently overwritten.
- Synthetic metrics characterize this generator/rule set, not actual SOC effectiveness. False positives remain visible.
