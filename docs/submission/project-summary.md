# SAT-SA — Supervisory Analytics Tool for SOC Assessment

NCIIPC assesses the cyber resilience of Critical Sector Entities (CSEs) partly by manually examining samples of SOC alerts and case-management records. Those reviews reveal operational weaknesses that policy documents and KPI dashboards can miss, but manual sampling is difficult to scale. SAT-SA is a local, offline supervisory prototype that helps an examiner decide **which entities and source records to review first, and why**. It is not a SIEM, a real-time monitor, or an automated compliance decision maker. Only a human examiner can record a supervisory outcome.

SAT-SA ingests structured CSV/JSON submissions and preserves them as immutable, hashed dataset versions. Its deterministic analytics cover eight supervisory families: threat detection, investigation, escalation, incident response, security operations, governance and oversight, operational discipline, and cyber resilience. They identify potential execution gaps—such as unusually fast closure of high-severity alerts, limited investigation evidence, missing escalation records, recurring asset alerts, and closure bursts—and negative space, including absent expected monitoring evidence and unusually low activity among matched peers.

Each indicator explains the observation, expectation or threshold, method, confidence, data completeness, and reason for review, with references to underlying records. A review queue combines overlapping indicators into prioritized samples and shows the contributions to each priority. Examiners can compare assessment periods, inspect a printable report, record human decisions, and follow the audit trail.

The core product runs locally through Docker Compose with no runtime Internet, cloud, SaaS, or external AI dependency. Its analytics do not call an AI provider. An isolated-network verification blocked external connections while the local workflow remained functional. The optional public deployment below is **a separate, synthetic-only demonstration path**.

On the seeded synthetic dataset, the completed run covered **8 pseudonymous CSEs, 13,886 records, and 25 entity-level indicators**. Against separately stored injected labels, post-run selection recall was **95.59%**, precision **55.86%**, and source-reference traceability **100%**. These figures measure synthetic patterns, **not** effectiveness on real SOC submissions or parity with NCIIPC expert review. The current repository check passed **109 Python tests**; frontend unit and browser tests are also included. Million-record throughput, blinded expert validation, and production security accreditation remain unverified.

- **Source code:** https://github.com/nischala755/SAT-SA
- **Live synthetic demo:** https://sat-sa-demo.tail2e8b39.ts.net/
- **Demo caution:** The live address uses a free Tailscale Funnel from a local Windows computer. It is available only while that computer, Docker Desktop, and Internet connection are running. Use synthetic data only; do not upload restricted CSE evidence or treat the URL as a production/NCIIPC deployment.
- **Video:** The repository contains a [49-second silent walkthrough](demo-walkthrough.mp4) and a [2–2.5 minute narration script](demo-script-2-5-min.md). No YouTube link has been provided or verified.

## Run and check locally

Install Docker Desktop with Compose and Git. The initial image build needs access to base images and dependency packages, or a prepared offline cache. From PowerShell:

```powershell
git clone https://github.com/nischala755/SAT-SA.git
cd SAT-SA
docker compose up --build --wait -d
docker compose ps
```

Open **http://127.0.0.1:3001**. The page should show **Backend connected**. Check the storage-backed status and API health:

```powershell
Invoke-RestMethod http://127.0.0.1:3001/api/status
Invoke-RestMethod http://127.0.0.1:8001/api/v1/health
```

Expect `ok: true` with `health.storage_ready: true` from the first endpoint and `status: ok` with `storage_ready: true` from the second. A fresh local demo volume initializes a synthetic dataset and a real analytics run; the seven datasets observed in the current development volume include prior testing and are not a fresh-install default. Keep the `sat-sa-data` volume: **do not run `docker compose down -v`** unless you intend to delete local evidence, reviews, and audit history. For deployment and validation limits, see [the README](../../README.md) and [verification record](verification.md).
