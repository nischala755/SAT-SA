# SAT-SA

Supervisory Analytics Tool for SOC Assessment

SAT-SA is intended to help NCIIPC supervisors examine periodic submitted SOC evidence. The product chain is submitted evidence → normalization → supervisory analytics → evidence gaps/anomalies → review prioritization → human examination → auditable supervisory decision.

**Phase 1 only:** runnable application shell, live backend/storage status, canonical domain contracts, local DuckDB metadata/audit persistence, immutable Parquet evidence and a deterministic synthetic dataset. There is no ingestion wizard, analytical engine, dashboard, review ranking or decision workflow yet. No analytical results are fabricated.

## Requirements and architecture

Authority: [problem statement](docs/problem-statement.md), [approved architecture](docs/architecture.md), [AGENTS.md](AGENTS.md), then [Phase 1 plan](docs/superpowers/plans/2026-09-27-phase-1.md). AGENTS.md is currently empty and has been preserved.

Next.js/TypeScript serves the application shell and a same-origin status proxy. FastAPI/Pydantic owns the status API. Repository interfaces separate local DuckDB metadata from immutable Parquet evidence. Python analytics packages are boundaries for later implementation. One process owns metadata writes; stop the API before running a metadata-writing CLI.

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

The [verification report](docs/phase-1-verification.md) contains actual command results and acceptance gaps. No precision, recall or ranking effectiveness is claimed before analytics exist.

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

`SAT_SA_STORAGE_ROOT` selects local storage; `SAT_SA_DEMO_SEED` selects the deterministic seed before initial generation. `SAT_SA_DEMO_MODE` must be true in Phase 1: non-demo mode fails closed because production authentication is not implemented. No login credentials are required for the local synthetic demonstration. Never use Phase 1 with real restricted SOC submissions or expose it beyond the controlled host.

`config/defaults.json` contains documented future analytical configuration. No configured threshold is executed in this phase. See [data dictionary](docs/data-dictionary.md), [methodology boundaries](docs/analytics-methodology.md) and [validation methodology](docs/validation-methodology.md).

The synthetic generator builds a bounded demonstration dataset in memory. This is not a tested million-record importer. The evidence reader applies entity filters and pagination in DuckDB; later ingestion needs streaming/chunking. Filesystem administrators can modify local files; hashes detect altered artifacts during verification/bootstrap but are not cryptographic signing or tamper-proof audit storage. Encryption at rest is a deployment-managed encrypted-volume responsibility.
