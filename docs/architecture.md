# SAT-SA architecture proposal

## Authorized completion addendum — 2026-09-27

The user has authorized phases 2–10 and the local summary design. Optional AI summaries are isolated CLI operations, not analytics, scores or decisions. Qwen runs through loopback Ollama. The user additionally requested an optional Mistral provider: it requires explicit cloud consent and an environment credential, and sends only the selected evidence. This is a documented exception to the earlier blanket prohibition on external calls; default application operation remains fully local and independent of AI. No key is committed. Summary drafts require human source verification. The historical Phase 1 authorization below is superseded by this addendum.

Status: approved by the user on 2026-09-27. Implementation is currently authorized for Phase 1 only, subject to the implementation-plan review. The supplied problem statement governs functional requirements; this document governs architecture and implementation boundaries; AGENTS.md governs engineering behaviour and agent constraints.

## Purpose and acceptance

SAT-SA helps NCIIPC supervisors select entities and records for manual examination of periodic SOC submissions. Analytical indicators are not determinations of non-compliance. The governing requirements are the supplied SAT-SA brief, including all ten implementation phases and its final acceptance criteria.

The central working flow is Overview → Entity → Signal → Evidence → Review decision. A second flow imports a submission, validates and normalizes it, executes analytics, and exposes reproducible results. Both must work without runtime Internet access.

## Architecture decision

Recommended: a modular monorepo with Next.js/TypeScript frontend, FastAPI/Pydantic API, and Python analytics using DuckDB and Parquet. A single local worker owns database writes and executes persisted jobs. The API accesses storage through repositories; analytics accept normalized inputs and configuration without depending on HTTP or UI code. Local frontend assets and system fonts avoid runtime CDN dependencies.

Alternative: PostgreSQL metadata plus DuckDB analytics from the outset provides stronger concurrent transactional access but adds deployment and migration work. Preserve this migration route through repository interfaces. An embedded single-process application is simpler to package but departs from the preferred architecture and offers less frontend/API separation.

Deploy the recommended prototype as web and API/worker containers with persistent local volumes. Serialize embedded database writes; do not imply unrestricted concurrent DuckDB writers. Millions-of-record readiness requires measured benchmarks, columnar queries, pagination and bounded-memory ingestion, not merely the choice of database.

## Domain and provenance

Typed normalized models cover CSEs, alerts, cases, assets and investigation events with the fields in the brief. Every record is tenant/entity scoped and carries source filename, source row or record identifier, batch ID and transformation version. Cross-record joins use entity ID as well as record ID. Preserve raw submitted files locally with hashes and access controls; do not ingest free-form investigation notes by default.

Datasets are immutable versions. Runs reference a dataset hash, exact configuration snapshot and hash, analytics/software versions, assessment period, timestamps, row counts and result counts. Review actions append actor, role, time, decision and note to the audit trail without rewriting analytical evidence.

## Ingestion

The wizard accepts CSV and JSON exports, detects format, maps columns, previews a bounded sample, validates rows and relationships, reports rejected records, normalizes and commits a versioned batch. Database-export support uses these structured formats; REST ingestion uses an explicitly configured internal endpoint adapter, disabled by default. No arbitrary server-side URL fetching.

Apply upload size and record limits, safe generated storage names, allowed formats, strict parsing and field validation. Show missingness and unresolved references. Distinguish absent optional evidence from invalid records. Imports and analytics are persisted jobs with visible progress and error states; failed work cannot appear as a successful complete dataset.

## Analytics and expectations

Independent versioned modules cover all eight signal families: detection, investigation, escalation, response, operations, governance, discipline and resilience. Initial implementations use deterministic counts, durations, recurrence, concentration and robust peer/historical comparisons. Thresholds, severity mappings, minimum sample sizes and expectation rules live in versioned JSON configuration and are documented as prototype defaults.

Each result exposes observed facts, inferred signal, a review hypothesis, evidence references, calculation, thresholds, strength, completeness, sample size and confidence separately. Unsupported analyses return explicit unavailable reasons. Zero activity alone does not establish a monitoring failure.

The evidence-gap engine evaluates explicit expectations for monitored assets, categories, escalation, investigation records and historical/peer activity. Results show expected evidence, observed evidence, gap, expectation source and sufficiency. Missing inventory disables coverage analysis. Missing escalation evidence is described as missing evidence, not proof no escalation occurred.

Peer cohorts use sector, declared peer group, criticality and comparable size/volume. Exclude the subject entity from its peer baseline. Show cohort size, median, percentile, IQR/MAD where appropriate and historical values. Suppress unstable comparisons when minimum samples are unmet; avoid competitive rankings of entities.

The optional metric-integrity module links apparently healthy closure metrics to weak supporting evidence without inferring intent.

## Prioritization and review

Rank finite review samples with documented contributions for severity, corroborating signals, evidence strength, novelty, recurrence and peer deviation. Display the full selection rationale and suggested review objective. Deduplicate overlapping samples and use deterministic tie-breaking.

Supervisors can accept, dismiss, explain, confirm a concern, mark false positive or insufficient evidence, request further investigation and add notes. Only authorized human actions create confirmed findings. Analytical runs never make that transition automatically.

## Interface and API

Use restrained light enterprise styling, compact cards, readable tables, navigation, filters, tabs and an evidence drawer. Implement overview, entity list/detail, review queue, signal explorer, source evidence, ingestion, validation and audit views. Share assessment-period context and expose loading, empty, insufficient-data and failure states.

FastAPI supplies typed, versioned endpoints from the brief and OpenAPI documentation. Lists use server-side filtering and pagination; evidence records are fetched on demand. The browser never downloads the entire analytical dataset. All displayed totals and charts derive from stored data and analytical outputs.

## Synthetic data and validation

A seeded generator creates eight pseudonymous CSEs across multiple sectors and peer groups, twelve months, thousands of alerts, hundreds of cases, assets and investigation events. Inject all ten requested patterns, including a healthy control entity. Store ground truth separately from analytics inputs to prevent label leakage.

Validate precision, recall, false-positive rate, coverage, Precision@20, Recall@20, ranking quality and evidence traceability against a clearly defined labelled universe. Report denominators and unavailable metrics. Compare sampling yield with a seeded random baseline. Any estimated time savings must declare assumed review times; do not present them as measured examiner productivity. Keep synthetic and human-reviewed validation results separate.

## Security and offline deployment

Configure an explicit authentication boundary and enforce reader, examiner and administrator permissions server-side. A conspicuous demo mode may use documented synthetic identities; production mode must reject missing authentication configuration. Do not trust browser-supplied roles or user IDs. Persist audit records for imports, runs and supervisory decisions.

Use local storage and deployment-managed encrypted-volume hooks; do not claim application encryption unless implemented. No committed secrets, telemetry, remote fonts or external AI/API dependencies. Building images may need dependencies; an air-gapped deployment needs prebuilt image archives and documented load/start commands. Runtime must be tested with external networking unavailable.

## Implementation sequence

1. Repository, typed models, architecture, seeded dataset and a runnable health endpoint.
2. Real ingestion, normalization, data quality and provenance.
3. Versioned deterministic signals across the eight families.
4. Explicit negative-space expectations and sufficiency handling.
5. Peer and historical baselines with robust statistics.
6. Transparent prioritization and persistent manual reviews.
7. Frontend dashboards, filters and evidence drill-down.
8. Label-based validation and sampling comparison.
9. Authentication boundary, auditability, offline packaging and deployment hardening.
10. Demo flow, accessibility, visual verification and documentation.

Keep the application runnable after each phase. Prefer a narrower working implementation over nonfunctional controls. Record any remaining acceptance gaps explicitly.

## Verification

Use Pytest for domain, analytics, ingestion and API tests; Vitest for meaningful frontend behavior; end-to-end smoke tests for import → run → evidence → review → audit and the seeded demo narrative. Every major signal needs a positive fixture and a normal/sufficient-data counterexample. Test missing inventory, incomplete evidence, invalid timestamps, cross-entity references, duplicate uploads, persistence, permissions and deterministic replay. Run the application and inspect important UI flows before claiming completion.

Deliver README, analytics methodology, data dictionary, validation methodology and deployment documentation alongside this architecture document. Report actual test and validation results, not expected results.
