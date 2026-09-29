# Submission revision verification — 2026-09-29

Environment: Windows PowerShell; Python 3.12.10; Node 24.18.0; npm 11.16.0; Docker 29.6.1; Compose v5.1.4; Edge Playwright channel. The app uses Next.js 16.3.6, React 19.3.0, FastAPI and DuckDB versions pinned in the repository lockfiles. Commands below ran from the repository root unless noted. Exit code **0** means completed successfully.

| Exact command | Exit | Observed result |
| --- | ---: | --- |
| `.venv\Scripts\python.exe -m pytest -q` | 0 | 108 passed, one upstream Starlette/httpx deprecation warning. |
| `.venv\Scripts\python.exe scripts/export_contracts.py --check` | 0 | 26 generated contract artifacts fresh. |
| `npm test` in `apps/web` | 0 | 6 Vitest tests passed. |
| `npm run typecheck` in `apps/web` | 0 | TypeScript clean. |
| `docker compose up --build --wait -d` | 0 | API and web images rebuilt; both healthy. |
| `npm run test:e2e -- --workers=1` in `apps/web`, with `SAT_SA_WEB_URL=http://127.0.0.1:3001` | 0 | 7 browser tests passed, including backend outage/retry, evidence/review/audit, import and report. |
| `docker compose stop api` | 0 | Stopped metadata writer before generating a second dataset. |
| `docker compose run --rm --no-deps api python scripts/generate_demo.py --seed 20260927 --assessment-year 2024 --output /var/lib/sat-sa/evidence/demo-2024 --labels-output /var/lib/sat-sa/ground_truth/demo-2024 --register /var/lib/sat-sa/metadata.duckdb` | 0 | Immutable 2024 dataset registered; hash `574def4e7a2af971d5316aab7fc03de17b77e9dbd127cc977167a95e4ae0a866`. |
| `docker compose start --wait api` | 0 | API healthy; 2024 analytics job completed. |
| `node scripts/render-architecture.mjs` in `apps/web` | 0 | Architecture PDF created; 2 pages, 328 and 395 extracted words. |
| `node scripts/render-presentation.mjs` in `apps/web` | 0 | Technical presentation created; 5 pages. |
| `node scripts/export-sample-report.mjs` in `apps/web` | 0 | Actual synthetic report printed to PDF; 6 pages; first page starts with the report, not the site shell. |
| `node scripts/record-demo.mjs` in `apps/web` | 0 | Browser video captured from real Compose UI; converted MP4 duration 49.48 seconds. |
| `.venv\Scripts\python.exe scripts/verify_containers.py` | 0 | Both containers' external probes blocked in an internal-only network; local shell, eight assets, frontend/backend request, analytics, evidence trace, review, outage UI and restart persistence passed. |
| `git diff --check` | 0 | No whitespace errors; Git noted only an existing CRLF/LF normalization. |

The local API returned 8 comparable CSEs for the distinct 2024 and 2025 runs. The selected 2025 report returned 25 actual indicators and 3 pre-existing recorded human decisions at that check. The frontend status proxy returned `ok: true`, backend `status: ok`, `storage_ready: true`. After the final offline verifier restored normal Compose, both services were healthy and seven dataset versions were registered in this reused local volume. The isolated check recorded 36 persisted audit events after restart. These local volume counts include previous testing and are **not** fresh-install defaults.

The 2024 generator was also run twice into separate ignored `artifacts/submission-a` and `artifacts/submission-b` directories with the same seed/year. Both reported the same dataset hash above; all eight artifact hashes matched. Existing generator tests cover different seeds and default-year byte reproducibility. Ground-truth labels remained under a separate tree.

Artifact QA: both PDF page counts were read with PyMuPDF and every page was rendered and visually inspected. The MP4 was inspected at 3, 15, 30 and 42 seconds; it shows the actual local overview, source evidence drawer, period comparison and validation. Video duration was read from the H.264 MP4 by the local `imageio-ffmpeg` binary. The architecture and slide HTML load only local assets and system fonts.

**Remaining gates:** The isolated override proves offline operation of the core, but normal Compose does not block egress by itself. No large-dataset throughput claim, expert manual-review comparison, NCIIPC accreditation, production SSO/MFA, successful live Mistral response, live Render deployment, or editable PPTX has been verified. The short video has no narration; the companion script supplies presenter lines.
