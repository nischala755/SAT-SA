# SAT-SA completion implementation plan

> **For agentic workers:** Use superpowers:executing-plans task by task.

**Goal:** Complete the approved supervisory prototype and optional summary tools, with actual verification.
**Architecture:** Preserve Next.js/FastAPI, local Parquet and single-owner DuckDB repositories. Deterministic analytics are independent of optional AI. Persist jobs, runs and human actions. Use server-owned demo identities or configured bearer identities.
**Tech Stack:** Existing Python, Pydantic, DuckDB, React and TypeScript; standard-library HTTP for optional summaries.
**Spec:** docs/problem-statement.md, docs/architecture.md, docs/local-qwen-design.md.

## Authorization and constraints

The user approved the summary design and explicitly authorized all remaining phases without intermediate approval stops. Execute natively in the existing dedicated branch. New Mistral exception is opt-in only, credentials from environment, no core cloud dependency. Never expose labels in evidence APIs. No fabricated findings or results. Record incomplete verification honestly.

## Review focus

Cross-CSE collisions; malformed/oversized ingestion; lost jobs after restart; reader write attempts; missing-data/peer denominator errors. Each is covered in the owning task tests.

## Tasks

- [ ] 1. Summary adapters: `analytics/sat_sa/assistance/summary.py`, `scripts/summarize_evidence.py`, `tests/test_summary.py`. Test allowlists, scoped inputs, unavailable/malformed provider, explicit Mistral opt-in and no secrets in output. Implement `draft_summary(root, dataset_id, cse_id, record_type, limit, provider)`; verify real Qwen and attempt configured Mistral with synthetic inputs only.
- [ ] 2. Ingestion: `analytics/sat_sa/ingestion/service.py`, contracts and API. Test CSV/JSON mapping, preview, lifecycle errors, provenance, cross-entity reference validation, bounded payloads and duplicate import. Implement `preview_submission` and immutable publication with persisted job/error state and raw source hash.
- [ ] 3. Analytics/negative space/peers: versioned independent rule modules, central JSON thresholds, pure deterministic orchestrator. Test positives and sufficient normal counterexamples, missing inventory, peer exclusion, recurrence windows and output reproducibility. Persist config/hash, evidence and run provenance.
- [ ] 4. Prioritization/validation: deterministic deduplicated review samples with additive documented factors, labelled evaluation isolated from analytical inputs and seeded random comparison. Test denominators, ranking, traceability and manual review outcomes.
- [ ] 5. Persistence/API/auth: typed routes for datasets, entities, signals, queue, evidence, trends, peers, ingestion, jobs, runs, validation, reviews and audit. Test real storage/restart, reader denial, identity spoofing, stale cross-run decisions and visible failures. Persist jobs before dispatch on one local executor.
- [ ] 6. UI: overview, entity assessments/detail, filtered signals, paged evidence, review decisions, ingestion mapping/preview, validation and audit views. Use real API data, visible loading/error/empty states, semantic controls and local styles. Test browser import/run/evidence/review/audit and failure states.
- [ ] 7. Delivery: regenerate contracts, full test/build suite, real Qwen, containers, blocked-egress core run, restart persistence, accessibility/visual checks. Update README, methodologies, deployment and completion verification with exact results. Independent final review, fix material findings with regression tests, commit and push.

Each task uses a failing regression test before implementation, runs relevant tests afterward and records results in `docs/completion-ledger.md`. Keep Phase 1 verification as a historical snapshot.
