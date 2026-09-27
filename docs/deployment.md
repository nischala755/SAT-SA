# Phase 1 local deployment

Use the exact native and Docker commands in README. `requirements.lock` and `apps/web/package-lock.json` lock tested dependencies. Build-time package registries and base-image pulls are distinct from runtime; archive the resulting images for offline deployment. Runtime containers use only bundled code, system fonts, local CSS/JS and local data.

The API runs one worker. A startup bootstrap generates or verifies the local demo and registers it transactionally, then exits before the API acquires its database connection. Multiple API workers or concurrent CLI writers are unsupported. Repository interfaces preserve a later PostgreSQL migration boundary.

Container filesystem roots are read-only. Temporary files use tmpfs; data uses the named volume. The API runs as UID/GID 10001 and the web process as the image's unprivileged node user. Published ports bind to 127.0.0.1. Both containers join one local bridge. No external model, HTTP adapter or telemetry endpoint is configured.

`docker compose stop` preserves the volume. `docker compose up --pull never --no-build --wait` restarts prepared images without fetching dependencies. Do not delete the volume to resolve an immutable-version mismatch; use a separately named deployment/volume when intentionally creating another demo version.

Host backups must preserve both metadata and evidence while the API is stopped. Encryption-at-rest support is provided by mounting storage from the organization's encrypted filesystem; this prototype does not implement application-level encryption, key management, identity federation or tamper-evident audit signing. Non-demo mode is rejected until authentication is implemented in a later authorized phase.

Deployment-plan adjustment: Docker Desktop 29.6.1 left host port bindings empty for an internal-only network, despite healthy containers. Normal Compose therefore uses a standard bridge for localhost access. `compose.offline.yaml` changes it to an internal-only network for verification, where container-local HTTP checks verify the frontend, bundled assets and backend while external TCP probes fail. Browser tests separately block and record nonlocal origins. Normal Compose does not enforce an egress firewall; use the controlled host/network boundary in deployment. This changes packaging details from the plan, not the approved two-container application architecture.

Verification must establish successful frontend/backend requests while container external-network probes fail. Merely reading `internal: true` is not proof of offline operation; see the phase verification report for actual outcomes and limits. The verification script restores normal Compose even if an isolated check fails.

Primary references consulted during implementation: [Next.js installation](https://nextjs.org/docs/app/getting-started/installation), [DuckDB concurrency](https://duckdb.org/docs/stable/connect/concurrency), [Pydantic types](https://docs.pydantic.dev/latest/api/types/). These are engineering references only; the deployed application does not request them.
