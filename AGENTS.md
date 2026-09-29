# AGENTS.md — SAT-SA Engineering Instructions

## Project

SAT-SA — Supervisory Analytics Tool for SOC Assessment.

SAT-SA is a supervisory analytics platform for analysing periodic SOC alert and case-management evidence from Critical Sector Entities.

The system supports expert supervisory assessment.

It does not replace a SOC, SIEM, SOAR, or human supervisory judgement.

---

# 1. Prime Directive

Build the simplest technically credible system that solves the stated supervisory problem.

Prioritize, in order:

1. Correct supervisory functionality.
2. Evidence-backed analytics.
3. Explainability.
4. Data quality and traceability.
5. Usability.
6. Scalability.
7. Security and offline deployment.
8. Visual polish.
9. Novelty.

Never sacrifice analytical correctness for visual novelty.

---

# 2. Architecture Rules

Use a modular architecture.

Preferred stack:

Frontend:

* Next.js
* React
* TypeScript
* Tailwind CSS
* shadcn/ui or equivalent

Backend:

* FastAPI
* Python
* Pydantic

Analytics:

* Python
* DuckDB
* Parquet
* Pandas/Polars where justified

Application metadata:

* PostgreSQL where needed

Deployment:

* Docker Compose

All components must support offline execution.

Do not add cloud services.

Do not add external APIs.

Do not add SaaS dependencies.

Do not make runtime requests to the Internet.

---

# 3. Modularity

Separate:

* ingestion
* normalization
* data quality
* signal detection
* negative-space analysis
* peer analysis
* prioritization
* validation
* API
* presentation

Analytics must not depend on React components.

UI components must not contain analytical calculations.

API routes must not contain complex analytics logic.

---

# 4. Analytics Rules

Every signal must answer:

1. What was observed?
2. What was expected?
3. How was expected behaviour derived?
4. How large is the deviation?
5. How much evidence supports it?
6. Is the data sufficiently complete?
7. Why should a supervisor care?
8. What records should the supervisor inspect?

A signal must be reproducible.

A signal must have a stable identifier.

A signal must have a documented methodology.

---

# 5. Language Rules

The application must use conservative supervisory terminology.

Prefer:

* potential concern
* review indicator
* evidence gap
* anomaly
* deviation
* requires review
* insufficient evidence
* data quality limitation

Avoid:

* malicious
* fraudulent
* negligent
* incompetent
* intentional manipulation

unless entered as an explicit human supervisory determination.

Do not infer intent.

---

# 6. Negative Space

Negative-space analysis is a first-class capability.

Never claim that an absence proves a control failure.

Instead express:

Expected evidence:
X

Observed evidence:
Y

Gap:
Z

Basis for expectation:
Historical / peer / asset inventory / configured requirement

Confidence:
High / Medium / Limited

If required input data is unavailable, report:

"Analysis unavailable due to insufficient evidence."

Never manufacture missing data.

---

# 7. Statistics

Prefer robust, explainable statistics:

* median
* percentile
* IQR
* MAD
* rolling averages
* historical baselines
* peer distributions

Use ML only where it adds measurable value.

Avoid deep learning unless explicitly justified.

Never introduce an opaque model merely to call the system AI-powered.

---

# 8. Thresholds

Do not hard-code business thresholds throughout source code.

Centralize them.

Configuration must be versioned.

Every threshold must have:

* name
* purpose
* default value
* unit
* rationale
* applicable population

Do not treat default thresholds as universal truth.

---

# 9. Data Provenance

Every analytical finding must be traceable to source records.

Preserve:

* ingestion batch
* source file
* source record identifier
* normalized record identifier
* analytics version

Do not discard provenance during transformation.

---

# 10. Scoring

Do not create one arbitrary "AI risk score."

If aggregation is required, call it an:

"Supervisory Attention Indicator"

and show its components.

Example:

Attention indicator derived from:

* 3 high-priority signals
* 2 negative-space indicators
* 1 major peer deviation
* 96% data completeness

The user must be able to drill into the components.

---

# 11. Review Prioritization

Review prioritization is a recommendation system for human sampling.

It must never automatically determine that a CSE has failed a control.

Every recommendation must explain:

* why selected
* which signal triggered it
* evidence strength
* data completeness
* severity
* peer deviation
* recurrence
* suggested review question

---

# 12. UI Rules

The interface must look conventional and professional.

Use:

* neutral background
* restrained blue/slate palette
* conventional tables
* filters
* tabs
* drawers
* breadcrumbs
* standard charts
* clear typography

Do not use:

* neon cybersecurity aesthetics
* hacker imagery
* excessive gradients
* glassmorphism
* glowing cards
* animated backgrounds
* excessive AI icons
* unnecessary 3D charts

Avoid the visual appearance of a generic AI-generated dashboard.

---

# 13. UX Principle

The main user question is:

"What requires my attention and why?"

Every important screen should support that question.

Prefer evidence density over decorative visualization.

---

# 14. Dashboard Rules

Never create a chart merely because a chart is possible.

Every visualization must answer a supervisory question.

Examples:

Good:
"How does this entity's investigation duration compare with peers?"

Bad:
"Investigation duration chart."

Good:
"Which critical assets have no expected monitoring evidence?"

Bad:
"Asset distribution."

---

# 15. Performance

Design for millions of records.

Never send huge datasets to the browser.

Use:

* pagination
* aggregation
* server-side filtering
* DuckDB queries
* Parquet
* indexes
* asynchronous jobs

Avoid O(n²) algorithms where large datasets are expected.

Document expensive queries.

---

# 16. API Rules

Use versioned APIs:

/api/v1/...

Use Pydantic models for contracts.

Never return unstructured arbitrary dictionaries for core domain objects if a typed schema can be defined.

Expose OpenAPI documentation.

Return useful error messages.

---

# 17. Security

No secrets in source control.

Validate uploaded files.

Limit upload sizes.

Reject unsupported file types.

Sanitize filenames.

Avoid unsafe SQL construction.

Do not expose stack traces to end users.

Do not make outbound network calls.

Do not load remote JavaScript or CSS resources.

---

# 18. Testing

Every analytics module requires tests.

At minimum test:

* normal case
* obvious positive case
* borderline case
* missing-data case
* insufficient-sample case

For every known synthetic supervisory pattern, create a regression test.

Example:

`test_high_severity_fast_closure_signal()`

`test_missing_escalation_signal()`

`test_negative_space_monitoring_gap()`

`test_peer_deviation_signal()`

`test_metric_integrity_indicator()`

---

# 19. Ground Truth

The demo dataset must include ground-truth annotations.

Do not evaluate analytics using the same rules that generated the labels without acknowledging this limitation.

Where possible, include manually labelled examples.

Validation should distinguish:

* synthetic injected scenarios
* historical baseline scenarios
* manually reviewed scenarios

---

# 20. Validation

Measure:

* precision
* recall
* false-positive rate
* review coverage
* Precision@K
* Recall@K
* evidence completeness

For the review queue, focus on whether useful supervisory cases are surfaced early.

Do not optimize solely for aggregate anomaly-detection accuracy.

---

# 21. Demo Reliability

The demo is a first-class product requirement.

`docker compose up` should be sufficient to launch the local environment.

Provide a sample dataset.

Provide deterministic demo results where appropriate.

The main demo path must work without Internet access.

Demo path:

Overview
→ Entity
→ Signal
→ Evidence
→ Underlying records
→ Review decision
→ Validation

---

# 22. Three Differentiators

The product should emphasize no more than three.

Required:

1. Evidence Gap Engine.
2. Supervisory Review Prioritizer.

Optional:

3. Metric Integrity Analysis.

Do not add unrelated features simply to appear innovative.

---

# 23. AI/ML Policy

Do not use external AI.

Do not make the product dependent on LLMs.

If an offline model is introduced, it must have:

* model version
* training methodology
* feature definition
* hardware requirements
* inference method
* explainability
* reproducibility
* validation results

A deterministic/statistical solution is preferred when it performs adequately.

---

# 24. Documentation

Update documentation when architecture changes.

Required documents:

`README.md`

`docs/architecture.md`

`docs/analytics-methodology.md`

`docs/data-dictionary.md`

`docs/validation-methodology.md`

`docs/deployment.md`

Documentation must describe limitations honestly.

---

# 25. Coding Style

Prefer:

* small functions
* explicit names
* typed interfaces
* domain-oriented modules
* pure analytical functions where possible
* deterministic tests
* meaningful error messages

Avoid:

* giant files
* giant React components
* magic constants
* duplicated business logic
* unused abstractions
* premature microservices
* speculative infrastructure

---

# 26. Dependency Policy

Before adding a dependency ask:

1. Is it necessary?
2. Is it maintained?
3. Does it work offline?
4. Does it increase deployment complexity?
5. Can the requirement be implemented simply without it?

Prefer fewer dependencies.

---

# 27. Agent Behaviour

Before implementing:

1. Inspect repository.
2. Read this file.
3. Inspect existing architecture.
4. Identify incomplete work.
5. Run existing tests.
6. Make a small implementation step.
7. Run relevant tests.
8. Continue incrementally.

Do not rewrite working functionality without reason.

Do not create fake placeholder implementations for core requirements.

If a requirement cannot be completed, implement the smallest real version and document the limitation.

---

# 28. Definition of Done

A feature is done only when:

* implemented
* tested
* connected to the real application
* documented
* usable offline
* explainable where applicable
* covered by sample data where applicable

A screen that only displays hard-coded demo values is not considered implemented.

---

# 29. Final Quality Gate

Before declaring the project complete, verify:

[ ] Offline operation

[ ] No external AI dependency

[ ] No cloud dependency

[ ] Data ingestion works

[ ] Data validation works

[ ] Multiple CSEs supported

[ ] Multi-period analysis works

[ ] Detection signals work

[ ] Investigation signals work

[ ] Escalation signals work

[ ] Incident-response signals work

[ ] Security-operations signals work

[ ] Governance signals work

[ ] Operational-discipline signals work

[ ] Cyber-resilience signals work

[ ] Negative-space analysis works

[ ] Peer comparison works

[ ] Entity attention indicators work

[ ] Review prioritization works

[ ] Evidence drill-down works

[ ] Audit trail works

[ ] Validation works

[ ] Synthetic ground truth exists

[ ] Demo works end-to-end

[ ] UI looks conventional and professional

[ ] README is complete

[ ] Architecture documentation is complete

[ ] No unsupported claims are presented as facts

