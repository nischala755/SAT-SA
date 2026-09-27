# SAT-SA — Supervisory Analytics Tool for SOC Assessment

You are the principal software architect and implementation engineer responsible for building a production-quality prototype called:

**SAT-SA — Supervisory Analytics Tool for SOC Assessment**

Build the solution as a credible supervisory analytics platform for the National Critical Information Infrastructure Protection Centre (NCIIPC).

The goal is NOT to build another SIEM, SOC, SOAR platform, generic cybersecurity dashboard, or AI chatbot.

The goal is to build a **supervisory analytics system that analyses periodic SOC alert and case-management data and helps expert supervisors identify entities, controls, processes, and individual cases that deserve manual examination.**

The system must support human supervisory judgement rather than replace it.

---

# 1. Primary Objective

SAT-SA must enable an NCIIPC supervisor to:

1. Import structured SOC datasets from multiple CSEs.
2. Normalize heterogeneous data into a common analytical model.
3. Analyse alert, case, investigation, escalation, disposition, closure, and asset/inventory information.
4. Identify potential execution gaps.
5. Identify potential negative space / missing expected evidence.
6. Identify anomalous operational behaviour.
7. Compare entities with appropriate peers.
8. Produce entity-level supervisory risk indicators.
9. Prioritize entities and cases for manual review.
10. Explain every important finding using observable evidence.
11. Drill down from an entity-level finding to the underlying alerts/cases.
12. Preserve an audit trail of analytical results and supervisory actions.
13. Support trend analysis across time.
14. Allow supervisors to distinguish between:

* observed evidence,
* inferred signal,
* analytical hypothesis,
* confirmed supervisory finding.

The application must make it clear that analytics identify **indicators requiring supervisory attention**, not definitive findings of non-compliance.

---

# 2. Non-Goals

Do NOT build:

* A SIEM.
* A SOC.
* A real-time monitoring system.
* A centralized national SOC.
* A log aggregation platform.
* Packet capture analysis.
* Continuous telemetry collection.
* A cloud/SaaS service.
* A conversational AI assistant as the primary interface.
* An autonomous incident-response system.
* Automated punitive/compliance decisions.
* Black-box ML that cannot explain its results.
* Dependence on Internet connectivity.
* Dependence on OpenAI, Anthropic, Gemini, Azure, AWS, or any external AI API.

The application must be fully usable in an air-gapped NCIIPC-controlled environment.

---

# 3. Product Philosophy

Follow these principles throughout implementation:

### Evidence over speculation

Every finding must be grounded in measurable data.

Bad:

"Entity appears cyber immature."

Good:

"14 critical alerts were closed within 15 minutes during the assessment period. 11 had no linked escalation record. This is materially different from the entity's peer median of 2.1%."

### Signal over score

Scores may summarize evidence, but the underlying evidence must always be accessible.

### Human-in-the-loop

The tool recommends what a supervisor should inspect.

The supervisor decides whether the observation constitutes a supervisory finding.

### Conservative language

Use:

* Potential weakness
* Review indicator
* Evidence gap
* Anomalous pattern
* Requires supervisory review
* Deviation from peer baseline

Do not automatically use:

* Violation
* Negligence
* Fraud
* Malicious
* Non-compliant

unless such a determination is explicitly entered by an authorized human.

### Reproducibility

The same dataset, configuration, and analytics version should produce reproducible results.

### Explainability

Every score or finding must have a traceable calculation.

---

# 4. Recommended Technology Architecture

Use a modular monorepo.

Preferred architecture:

* Frontend: Next.js + TypeScript
* UI: React + TypeScript
* Styling: Tailwind CSS
* Components: shadcn/ui or equivalent conventional component system
* Charts: Apache ECharts or Recharts
* Backend API: Python FastAPI
* Analytical processing: Python
* Analytical data engine: DuckDB + Parquet
* Metadata/application database: PostgreSQL
* Background jobs: Celery/RQ or a simple database-backed job abstraction for the prototype
* Validation/testing: Pytest + Vitest
* Containerization: Docker / Docker Compose
* API specification: OpenAPI
* Data validation: Pydantic
* Data processing: Pandas/Polars where appropriate

If implementation simplicity becomes important, DuckDB may initially handle both analytical storage and much of the metadata workload, but the architecture must preserve a clean repository/service boundary so PostgreSQL can be introduced without rewriting analytics.

Do not introduce Kubernetes unless genuinely required.

Do not introduce microservices merely for architectural appearance.

The system should be modular internally but deployable as a small number of containers.

---

# 5. Repository Structure

Create a structure approximately like:

/apps
/web
/api

/packages
/shared-types
/analytics-contracts

/analytics
/ingestion
/normalization
/signals
/negative-space
/peer-analysis
/risk
/prioritization
/validation

/data
/sample
/schemas

/docs
architecture.md
analytics-methodology.md
data-dictionary.md
validation-methodology.md
deployment.md

/tests
/unit
/integration
/analytics
/fixtures

/scripts

/docker

README.md
AGENTS.md

Keep domain logic independent from UI code.

---

# 6. Core Domain Model

Design normalized entities around:

## CSE

Fields should include:

* cse_id
* name / pseudonymized name
* sector
* peer_group
* criticality
* assessment_period

## Alert

Include:

* alert_id
* cse_id
* timestamp
* severity
* source
* alert_category
* rule/use_case
* asset_id
* asset_criticality
* acknowledgement_timestamp
* investigation_start_timestamp
* case_id
* disposition
* closure_timestamp
* closure_reason
* escalation_required
* escalation_timestamp
* escalation_type

## Case

Include:

* case_id
* cse_id
* opened_at
* closed_at
* severity
* assigned_team
* investigator
* investigation_steps_count
* investigation_duration
* escalation_status
* escalation_timestamp
* root_cause
* remediation_status
* linked_alert_count
* closure_reason

## Asset

Include:

* asset_id
* cse_id
* criticality
* environment
* system_type
* monitoring_expected
* monitoring_source

## Investigation Event

Include:

* case_id
* timestamp
* event_type
* actor/team
* action
* evidence_reference
* notes_length
* outcome

Do not store sensitive raw investigation notes unless necessary for the prototype.

---

# 7. Data Ingestion

Support:

* CSV
* JSON
* database exports
* REST APIs where available

Build an ingestion wizard:

1. Upload dataset.
2. Detect format.
3. Validate schema.
4. Display column mapping.
5. Preview records.
6. Show validation errors/warnings.
7. Normalize.
8. Import.
9. Generate ingestion summary.

Example:

"Alerts imported: 1,245,830"

"Cases imported: 31,482"

"Records rejected: 327"

"Missing escalation timestamp: 4.2%"

"Unknown asset IDs: 1.7%"

The ingestion layer must preserve source provenance.

Each normalized record should be traceable to:

* source file
* source row / record identifier
* ingestion batch
* transformation version

---

# 8. Analytics Framework

Build analytics as independent, versioned signal modules.

Each signal should have:

* signal_id
* name
* category
* description
* severity
* confidence
* methodology
* thresholds
* evidence references
* calculation version

Example:

SIGNAL-DET-001

"High-severity closure velocity anomaly"

Category:
Detection / Investigation

Method:

Compare closure duration for high-severity alerts against:

1. entity's historical distribution,
2. peer distribution,
3. configurable absolute thresholds.

Evidence:

* alert IDs
* closure timestamps
* duration distribution
* peer percentile
* historical percentile

Never hard-code arbitrary thresholds without documenting them.

---

# 9. Required Supervisory Signal Families

Implement at minimum the following.

## A. Detection effectiveness

Signals such as:

* unusually low alert activity for critical assets
* missing expected alert categories
* abrupt changes in alert volume
* unusual distribution of alert severities
* critical assets without expected monitoring evidence
* concentration of detection activity in a small subset of assets
* unexplained monitoring coverage gaps

---

## B. Investigation quality

Signals such as:

* very short investigation durations
* repeated identical investigation patterns
* unusually low investigation activity
* high-volume cases with minimal investigation events
* repeated closure reasons
* high-severity cases lacking supporting investigation activity
* investigation workload inconsistent with alert volume

Avoid claiming that short investigations are inherently bad.

Treat them as review indicators.

---

## C. Escalation effectiveness

Signals such as:

* critical alerts closed without escalation
* delayed escalation
* inconsistent escalation behaviour across similar severities
* repeated missing escalation records
* entities with unusually low escalation rates
* severity/escalation mismatches

---

## D. Incident response

Signals such as:

* repeated alerts against the same asset without remediation evidence
* recurring incidents without root-cause closure
* high recurrence after closure
* long-running cases
* unresolved critical cases
* repeated closure without remediation status

---

## E. Security operations

Signals such as:

* unusual workload distribution
* repeated assignment patterns
* investigator concentration
* backlog growth
* closure bursts
* abnormal temporal patterns
* excessive reliance on a small set of analysts
* unusual after-hours patterns

These should remain descriptive.

Do not infer misconduct.

---

## F. Governance and oversight

Signals such as:

* repeated missing fields
* inconsistent case classification
* inconsistent severity/disposition combinations
* missing approval/escalation evidence
* repeated workflow exceptions
* incomplete audit trails

---

## G. Operational discipline

Signals such as:

* bulk closure patterns
* repeated closure reasons
* closure activity clustered near reporting deadlines
* unusually high same-day closure rates
* inconsistent timestamps
* records that technically satisfy a KPI but contain weak supporting evidence

---

## H. Cyber resilience

Signals such as:

* recurring incidents
* concentration of risk in critical assets
* monitoring gaps
* repeated failures without remediation
* sudden drops in detection activity
* operational degradation over time
* inability to explain major changes in security activity

---

# 10. Negative Space Engine

This is a major differentiator.

Do not limit analytics to "what happened."

Build a framework for detecting "what should reasonably have appeared but did not."

The engine should work using explicit expectations.

Example:

Asset inventory:

Critical assets = 100

Expected monitoring coverage = 100

Observed monitoring evidence = 73

Potential coverage gap = 27 assets

Another example:

Historical data shows that similar critical assets normally generate alerts from detection category X.

A subset generates zero category-X activity.

The system should produce:

"Potential negative-space indicator"

rather than:

"Monitoring failure."

The engine must support:

* expected activity baselines
* expected category presence
* expected escalation presence
* expected investigation records
* expected monitoring coverage
* expected peer activity
* historical baselines

Every negative-space finding must display:

Expected evidence
Observed evidence
Gap
Method used to derive expectation
Confidence / data sufficiency

---

# 11. Peer Benchmarking

Implement peer groups based on available metadata such as:

* sector
* entity size
* criticality
* environment
* alert volume
* asset count

Do not compare every CSE blindly against every other CSE.

Use robust statistics where appropriate:

* median
* percentile
* interquartile range
* MAD
* z-score only where statistically appropriate

Show:

Entity value
Peer median
Peer percentile
Historical value
Deviation

Avoid leaderboard-style presentation.

This is supervisory analysis, not competition.

---

# 12. Entity Supervisory Risk Profile

Create an entity profile page containing:

* Overall supervisory attention indicator
* Detection
* Investigation
* Escalation
* Incident Response
* Security Operations
* Governance
* Operational Discipline
* Cyber Resilience

Do NOT make this look like a simplistic "AI risk score."

Instead show:

"Attention indicators"

with evidence-backed categories.

For each category show:

* signal count
* high-priority indicators
* trend
* peer deviation
* evidence completeness

Allow the supervisor to inspect each underlying signal.

---

# 13. Supervisory Review Prioritizer

This is the second major differentiator.

Create a review queue that answers:

"Given limited supervisory time, what should I examine first?"

Each review recommendation should contain:

* entity
* alert/case
* reason for selection
* signal(s)
* evidence strength
* novelty
* severity
* peer deviation
* recurrence
* confidence
* suggested review objective

Example:

"Review Case C-10291"

Why:

* Critical severity
* Closed in 7 minutes
* No escalation record
* Same asset generated 6 similar alerts in previous 30 days
* Peer entities show materially longer investigation duration

The tool should not automatically declare a finding.

It should recommend the sample.

Allow supervisors to:

* accept for review
* dismiss
* mark as explained
* mark as confirmed finding
* mark as false positive
* add supervisory note

---

# 14. Metric Integrity Analysis

Implement as an optional analytics module.

Goal:

Identify cases where operational metrics appear healthy but supporting evidence is weak.

Example:

KPI:

"95% alerts closed within SLA."

Supporting evidence:

* unusually high closure bursts
* low investigation-event density
* repeated closure reasons
* critical cases lacking escalation evidence

Output:

"Metric integrity review indicator"

Do not call this "metric manipulation."

Do not infer intent.

The system is identifying a mismatch between the KPI and underlying operational evidence.

This feature should be highly explainable.

---

# 15. Anomaly Detection

Use conventional, explainable methods first.

Possible methods:

* IQR
* MAD
* percentile thresholds
* rolling baselines
* change-point detection
* isolation forest only where it materially adds value

Do NOT begin with deep learning.

Do NOT introduce an LLM unless a compelling offline use case emerges.

If machine learning is used:

* document training data
* document features
* document model
* document hyperparameters
* provide deterministic inference where practical
* version the model
* record model version with every result
* expose feature contributions or equivalent explanation
* allow supervisors to understand why an item was selected

A transparent statistical system is preferable to an impressive but unverifiable AI system.

---

# 16. Explainability

Every finding must support an evidence drawer.

Example:

FINDING:
High-severity alerts closed unusually quickly.

Evidence:

Observed:
Median closure = 11 minutes

Entity historical median:
84 minutes

Peer median:
71 minutes

Peer percentile:
4th percentile

Sample:
47 alerts

Critical alerts:
12

Escalated:
1

Data completeness:
96%

Method:
Peer + historical percentile analysis

This must be accessible directly from the UI.

---

# 17. Confidence and Data Sufficiency

Do not confuse anomaly strength with data quality.

Every finding should have:

Signal strength
Data completeness
Confidence
Evidence count

Example:

Signal strength: High
Data completeness: 98%
Evidence count: 126
Confidence: High

Or:

Signal strength: High
Data completeness: 41%
Confidence: Limited

This prevents supervisors from over-trusting incomplete submissions.

---

# 18. UI/UX Requirements

The UI must look like a serious government/enterprise supervisory application.

Do NOT make it look like:

* an AI chatbot
* a startup landing page
* a futuristic cybersecurity movie interface
* neon hacker graphics
* excessive gradients
* glassmorphism everywhere
* oversized cards
* unnecessary animations

Use a conventional enterprise design.

Recommended visual direction:

* neutral light theme
* white / slate / muted blue palette
* restrained accent colors
* clear typography
* dense but readable tables
* compact cards
* conventional navigation
* breadcrumbs
* filters
* tabs
* drawers
* tooltips
* evidence panels
* accessible charts

Use color sparingly.

Avoid using red everywhere.

High-risk/high-priority states may use restrained semantic colors.

---

# 19. Primary Screens

Implement these screens:

## 1. Supervisory Overview

Show:

* assessment periods
* CSE count
* total alerts
* total cases
* high-priority review indicators
* data quality
* trend summary
* attention distribution

## 2. Entity Assessment

Table of CSEs with:

* entity
* peer group
* alert volume
* case volume
* high-priority indicators
* negative-space indicators
* attention areas
* trend

Filters:

* sector
* peer group
* assessment period
* signal type
* priority

## 3. Entity Detail

Show the full supervisory evidence profile.

## 4. Review Queue

Ranked recommended samples.

## 5. Signal Explorer

Search/filter all analytical signals.

## 6. Evidence View

Detailed drill-down from signal to source records.

## 7. Data Ingestion

Upload and validate datasets.

## 8. Validation

Show how analytics performed against labelled/manual-review data.

## 9. Audit Trail

Show:

* analytics run
* dataset version
* configuration
* model/version
* timestamp
* result count

---

# 20. Important UX Detail

The application should make the supervisory reasoning chain visually obvious:

DATA
↓
SIGNAL
↓
EVIDENCE
↓
SUPERVISORY HYPOTHESIS
↓
MANUAL REVIEW

Do not collapse these into one "AI says risk is high" score.

---

# 21. Demo Dataset

Create a realistic synthetic dataset representing at least:

* 5–10 CSEs
* multiple sectors
* multiple peer groups
* 6–12 months
* thousands of alerts
* hundreds of cases
* critical and non-critical assets
* investigation events
* escalation records

Intentionally inject several known patterns:

1. Fast closure of high-severity alerts.
2. Repeated alerts against the same asset.
3. Missing escalation records.
4. Missing monitoring evidence.
5. Investigation-template repetition.
6. Low activity in a critical environment.
7. Peer deviation.
8. Closure bursts.
9. KPI/evidence mismatch.
10. One entity with genuinely healthy behaviour.

The synthetic data must contain ground-truth labels for validation.

Make the demo visually compelling but statistically plausible.

---

# 22. Validation Framework

Build a validation framework that compares analytical outputs with known injected patterns and manually labelled samples.

Metrics should include:

* precision
* recall
* false-positive rate
* coverage
* ranking quality
* evidence traceability
* time saved versus random/manual sampling

For review prioritization, evaluate:

"How many known supervisory signals appear in the top N recommended reviews?"

For example:

Precision@20
Recall@20

Do not optimize only for anomaly detection.

The core metric is:

**How effectively does SAT-SA direct scarce supervisory attention toward useful manual reviews?**

---

# 23. Manual Review Simulation

Create a demo workflow where an examiner can inspect:

Recommended sample
→ evidence
→ underlying records
→ supervisor decision

Supervisor decisions:

* Confirmed supervisory concern
* Explained / acceptable
* False positive
* Insufficient evidence
* Needs further investigation

Use these decisions as validation data.

---

# 24. Dashboard Design

Do not create 30 charts.

Prefer:

* 3–5 key KPI cards
* 1 trend visualization
* 1 attention distribution
* 1 review queue
* 1 evidence-gap visualization

The main dashboard should answer:

"What requires my attention?"

not:

"How many charts can we display?"

---

# 25. Security Requirements

Because this is designed for an NCIIPC-controlled environment:

* no external network calls
* no telemetry sent externally
* no analytics API calls
* no remote fonts
* no external CDN dependencies at runtime
* configurable authentication boundary
* role-aware architecture
* audit logging
* local storage
* encryption-at-rest hooks where deployment environment supports them
* secure file upload validation
* input sanitization
* no secrets committed to repository

The application must continue functioning when disconnected from the Internet.

---

# 26. Performance Requirements

Design for:

* millions of alert records
* hundreds of thousands of cases
* multiple CSEs
* multi-period analysis

Use columnar analytical storage and query engines appropriately.

Do not load entire datasets into browser memory.

Use:

* pagination
* server-side filtering
* aggregation
* indexed metadata
* asynchronous analytics jobs
* caching where useful

The UI should remain responsive.

---

# 27. Auditability

Every analytical run should store:

* run ID
* dataset/version
* analytics version
* signal configuration
* execution time
* records analysed
* findings generated
* software version

A supervisor should be able to reproduce why a finding existed.

---

# 28. Configuration

Thresholds must not be scattered throughout code.

Create configuration for:

* severity mappings
* peer groups
* expected monitoring rules
* minimum sample sizes
* anomaly thresholds
* escalation expectations
* negative-space expectations

Support YAML/JSON configuration.

Document all default thresholds.

---

# 29. Error Handling

Never silently fail.

Examples:

If asset inventory is missing:

"Negative-space coverage analysis unavailable: asset inventory not supplied."

Do not produce a fabricated coverage score.

If escalation data is incomplete:

"Escalation analysis confidence reduced due to 34% missing escalation records."

---

# 30. No Fake AI

Do not add an LLM simply because the project is labelled AI/analytics.

If a feature can be implemented using:

* deterministic rules
* statistical analysis
* peer benchmarking
* time-series analysis

prefer those methods.

Any AI/ML component must have a documented supervisory justification.

---

# 31. API Design

Create clean REST APIs such as:

GET /api/v1/entities
GET /api/v1/entities/{id}
GET /api/v1/signals
GET /api/v1/signals/{id}
GET /api/v1/review-queue
GET /api/v1/evidence/{id}
GET /api/v1/trends
GET /api/v1/peer-analysis
POST /api/v1/ingestion
POST /api/v1/analytics/run
GET /api/v1/analytics/runs
GET /api/v1/validation
POST /api/v1/reviews
GET /api/v1/audit

Use typed request/response schemas.

Generate OpenAPI documentation.

---

# 32. Testing

Implement:

* unit tests
* analytics tests
* API tests
* ingestion tests
* validation tests
* UI component tests
* end-to-end smoke tests

Every major signal should have synthetic test fixtures.

Example:

Given 10 critical alerts with 2-minute closure times and no escalation,
the high-severity closure anomaly signal should trigger.

Given complete and normal peer behaviour,
the signal should not trigger.

---

# 33. Documentation

Produce:

README.md
docs/architecture.md
docs/analytics-methodology.md
docs/data-dictionary.md
docs/validation-methodology.md
docs/deployment.md

README must contain:

* problem
* architecture
* features
* setup
* demo instructions
* sample credentials if applicable
* sample dataset
* analytics methodology
* validation results
* limitations

---

# 34. Demo Mode

Create a one-command demo environment.

For example:

docker compose up

Then:

1. application starts
2. sample dataset is available
3. analytics results are precomputed or generated
4. dashboard opens
5. reviewer can demonstrate:
   Overview → Entity → Finding → Evidence → Review Decision

The demo must not depend on Internet access.

---

# 35. Demo Narrative

Optimize the product around this demonstration:

"Instead of asking NCIIPC supervisors to manually search millions of records, SAT-SA first identifies where supervisory attention is most likely to produce useful findings."

Demo:

1. Show 8 CSEs.
2. Show overview.
3. Select one entity with several attention indicators.
4. Open "Critical alerts closed unusually quickly."
5. Show statistical comparison with historical and peer baseline.
6. Drill into the exact alerts.
7. Show missing escalation evidence.
8. Show recurring alerts against the same asset.
9. Open Negative Space.
10. Show critical assets with expected but absent monitoring evidence.
11. Add both findings to review queue.
12. Show prioritization rationale.
13. Record manual reviewer conclusion.
14. Show validation metrics.

This is the central product story.

---

# 36. What Counts as a "Wow Feature"

The application should have no more than three.

Required:

### Wow Feature 1 — Evidence Gap Engine

Detects absence of expected evidence using explicit baselines.

### Wow Feature 2 — Supervisory Review Prioritizer

Ranks the finite set of records an examiner should inspect, with transparent reasons.

### Optional Wow Feature 3 — Metric Integrity View

Shows mismatches between reported operational KPIs and underlying evidence.

Do not add unrelated AI features.

Do not add chatbots, autonomous agents, generative summaries, cyber attack simulation, threat intelligence feeds, or futuristic visualizations unless explicitly required later.

---

# 37. Visual Quality Bar

The final interface must look like software that could plausibly be deployed inside a government supervisory organization.

Prioritize:

* alignment
* spacing
* typography
* table quality
* filtering
* information density
* evidence traceability
* consistent interaction patterns

Avoid:

* excessive gradients
* glowing borders
* neon colors
* animated backgrounds
* giant numbers
* AI sparkle icons
* generic "AI-powered" copy
* unnecessary 3D visualizations

The product name should appear as:

SAT-SA

Subtitle:

Supervisory Analytics Tool for SOC Assessment

---

# 38. Implementation Strategy

Implement in phases.

PHASE 1:
Repository + architecture + data model + sample dataset.

PHASE 2:
Ingestion + normalization.

PHASE 3:
Core analytics signals.

PHASE 4:
Negative-space engine.

PHASE 5:
Peer benchmarking.

PHASE 6:
Review prioritization.

PHASE 7:
Frontend dashboards and drill-down.

PHASE 8:
Validation framework.

PHASE 9:
Auditability + deployment hardening.

PHASE 10:
Demo polish.

At the end of every phase, ensure the application remains runnable.

Do not create placeholder screens with fake functionality.

If a feature cannot be implemented fully, implement a smaller real version rather than a visually convincing mock.

---

# 39. Engineering Behaviour

Before writing substantial code:

1. Inspect the repository.
2. Read AGENTS.md.
3. Identify existing code and constraints.
4. Create/update architecture documentation.
5. Implement incrementally.
6. Run tests.
7. Run the application.
8. Verify important user flows.
9. Fix errors.
10. Only then polish.

Do not overwrite working code unnecessarily.

Prefer small, reviewable changes.

Do not introduce dependencies without justification.

---

# 40. Final Acceptance Criteria

The solution is complete only when:

* A user can import realistic CSE datasets.
* Data quality is visible.
* Analytics execute successfully.
* Multiple supervisory signal types are generated.
* Negative-space analysis works.
* Peer comparison works.
* Entity-level attention indicators work.
* Review prioritization works.
* Findings can be drilled into.
* Supporting evidence is visible.
* Manual reviewer decisions can be recorded.
* Audit information is retained.
* Validation results can be displayed.
* The entire system works offline.
* The demo works using synthetic data.
* No external AI/API is required.
* The application does not pretend that analytics are definitive supervisory findings.
* The interface looks like conventional enterprise/government software.
* The implementation is modular and scalable.
* Documentation is sufficient for another engineer to deploy the solution.

Most importantly:

**Do not optimize for the appearance of sophistication. Optimize for defensible supervisory usefulness.**
