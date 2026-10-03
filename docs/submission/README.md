# Smart India Hackathon submission packet

SAT-SA answers the NCIIPC supervisory assessment problem with a working, local, evidence-based prototype. The [submission-ready project summary](project-summary.md) includes the live synthetic demo and local deployment checks. The [demo QR code](live-demo-qr.png) is also available as a [scalable SVG](live-demo-qr.svg). Start with the [49-second walkthrough](demo-walkthrough.mp4), then inspect the [five-slide technical presentation](technical-presentation.pdf), [two-page architecture](architecture-2p.pdf), and [sample examiner report](sample-supervisory-report.pdf). The [repository README](../../README.md) has exact run and import steps. Editable HTML sources for the presentation PDFs and the [short demo narration](demo-script.md) and [2–3 minute narration](demo-script-2-3-min.md) and [2–2.5 minute narration](demo-script-2-5-min.md) are alongside the artifacts.

| Evaluation objective | Demonstrated path | Boundary |
| --- | --- | --- |
| Support supervisory assessment | Overview → entity → indicator → evidence → human review → audit | Human examiner owns decisions. |
| Execution gaps | Fast closures, limited investigation activity, missing escalation evidence, repeated templates, metric-evidence mismatch | Indicators require source/context review. |
| Negative space | Critical-asset and category expectations, low activity and absent escalation records | Absence does not prove control failure; missing inventory makes coverage unavailable. |
| Explainability | Observation, denominator, threshold, method, completeness, expectation and source references | Model-free deterministic rules; no opaque risk score. |
| Auditability | Dataset/run/configuration hashes, provenance, append-only reviews and audit events | No signed/tamper-evident audit or SSO. |
| Scale | DuckDB/Parquet, entity-scoped queries, pagination and asynchronous local jobs | Prototype currently caps loading at 100,000 records; million-scale throughput unverified. |
| Cross-period assessment | Two immutable runs compared by 30-day rates | Cohort change and absent entities are explicitly unavailable. |
| Validation | Separate seeded ground truth, synthetic metrics, random sampling baseline, human outcome counts | No blinded expert manual-review benchmark yet. |
| Offline deployment | Docker Compose images, local storage, bundled assets; isolated-network check | Normal Compose does not itself block outbound egress. |

The default system makes **no external AI or cloud call**. Optional Mistral and Render demonstration paths are separate, user-authorized exceptions and must not be used for restricted NCIIPC data. Local Qwen drafting is optional, never used by the signal engine. For a strict air-gapped evaluation, use the core Compose path without either provider.

## Reproduce the artifacts

The deck is PDF rather than PPTX. The browser scripts use the installed Playwright Edge channel and local HTML/image sources, without remote fonts or templates. From `apps/web`, run `node scripts/render-architecture.mjs`, `node scripts/render-presentation.mjs`, `node scripts/export-sample-report.mjs`, and, with the two demo periods prepared per README, `node scripts/record-demo.mjs`. The recording script creates WebM; the submitted MP4 is H.264 conversion using `imageio-ffmpeg` in the local authoring environment. The MP4 is 49.48 seconds, 1,115,885 bytes, and silent. The PDF handout is exactly two A4 pages; the technical presentation is exactly five landscape pages. The sample report is six A4 pages captured through the application's print stylesheet from a completed synthetic run.

For a live judge walkthrough, run `docker compose up --build --wait`, open `http://127.0.0.1:3001`, inspect CSE-01's source evidence, review the negative-space view, compare `demo-2024` with `demo`, open the report, and show validation and audit. The [verification record](verification.md) gives exact checks. No slide or video presents synthetic benchmark results as measured NCIIPC effectiveness.

## Estimated local prototype operation

Plan for a recent x86-64 host with Docker Compose, two CPU cores, 4 GiB RAM and at least 2 GiB free persistent storage **for the small demo**. These are conservative planning figures, not a tested minimum or large-scale sizing result. A 2026-09-29 idle snapshot showed API 126.3 MiB and web 52.26 MiB in Docker; the packaged 2025 evidence artifacts total 3,213,967 bytes. Peak import/analysis memory, sustained throughput, backup retention and million-record requirements must be measured against the intended NCIIPC hardware and submission mix. The DuckDB metadata store is single-writer; run only one API worker and stop it before a metadata-writing CLI.

## Expert validation gate

Before field use, obtain blinded manual-review labels from NCIIPC examiners on a representative, approved sample across sectors and periods. Freeze the dataset and rule configuration before evaluation. Compare top-K SAT-SA samples against current manual sampling using confirmed supervisory concerns per examiner hour, Precision@K, Recall@K where the labelled universe permits, false-positive burden, evidence completeness, reviewer agreement and missed-case analysis. Keep unreviewed cases out of recall claims. Record examiner time, disagreement resolution, threshold calibration and provenance. The repository's synthetic injected labels exercise implementation, but cannot establish parity with expert examination.
