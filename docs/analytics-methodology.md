# Supervisory analytics methodology

Analytics version `1.1.0`, configuration schema `1.0.0`. Outputs are review indicators, not compliance determinations. Analytics never use a language model or labels. Runs retain immutable dataset/configuration hashes, snapshots, timestamps, versions and record/result counts.

## Prototype defaults

Active thresholds live in validated `config/engine.json`. They are demonstration parameters, not NCIIPC policy or calibrated operational standards. A changed configuration requires a new run; previous results remain immutable.

| Rule | Observable predicate | Family and limitation |
| --- | --- | --- |
| fast_closure | High/critical alert closes within 15 minutes | Detection; short duration alone is not weak investigation |
| weak_investigation | Closed high/critical case has fewer than 2 submitted events | Investigation; absent records do not prove no work occurred |
| template_repetition | At least 10 cases share a closure reason and report fewer than 2 steps | Investigation; templates may be legitimate |
| missing_escalation | Closed alert requires escalation by field/severity; neither timestamp nor escalation record exists | Escalation; explicit expectation |
| recurrence | At least 4 alerts of a category on an asset within 30 days | Incident response; review remediation context |
| long_cases | Unclosed case is at least 30 days old at assessment end | Incident response; descriptive |
| workload_concentration | One investigator owns at least 80% of cases, minimum 10 cases | Security operations; no misconduct inference |
| missing_fields | Closed case lacks root cause or remediation status | Governance; export may be incomplete |
| closure_bursts | At least 5 cases close in one minute | Discipline; batch administration may explain it |
| monitoring_gap | Critical asset declares monitoring expected but has no submitted alerts | Resilience; activity is not a monitoring heartbeat |
| category_gap | Configured endpoint/identity/network category absent | Detection; applicability requires confirmation |
| low_activity | Alert volume below 25% of matched peer median | Resilience; exposure may explain differences |
| peer_deviation | High-severity median closure exceeds 3 times peer median | Operations; duration is not quality |
| metric_integrity | Fast closure intersects limited investigation events | Optional discipline module; no intent inference |

Missing inventory suppresses coverage with an unavailable reason. Missing closure times are excluded from duration calculations. Optional evidence is never invented. Reversed timestamps are rejected at ingestion.

## Peers, history and sufficiency

Peers match sector, peer group, criticality, declared entity size and the exact assessment window; exclude the subject. At least three values are required. Incompatible periods are suppressed rather than compared as raw counts. Report median, empirical percentile (fraction of peers less than or equal to the subject), inclusive IQR, MAD and signed deviation. No normality assumption is used. Asset-count/environment/volume matching is not yet implemented and is a comparability limitation.

Historical/current closure summaries divide the assessment period at its midpoint. This is within-period history, not an independently collected prior-period baseline. Monthly trends derive from submitted timestamps.

Strength, completeness and confidence are distinct. Strength is high when the matching fraction exceeds 50%, otherwise medium; this versioned presentation convention is not a probability. Each signal exposes a completeness basis: closure times for duration rules, expected investigation events for investigation rules, escalation evidence among eligible alerts, root-cause/remediation fields for governance, investigator identity for concentration, and asset links for recurrence. Confidence is limited below the sample minimum or below 80% relevant completeness. Fully present mandatory normalized fields do not establish completeness of the external submission. The entity table's completeness is separately the closed-alert fraction; ingestion missingness is per field/table. These conventions need operational calibration.

## Review prioritization

Deduplicate by CSE/type/record ID. Add visible contributions: severity (critical 40, high 30, medium 15, low 5), corroboration (10 per extra signal, cap 30), sufficient-evidence indicator (10), recurrence (10), peer deviation (10). Novelty contributes zero because prior-run comparison is unavailable. Ties sort by entity/type/ID. Points are review priorities, not probabilities or compliance scores. Every sample retains contributing signals and source references.

Only authorized human actions record confirmed concerns. Review events preserve actor, role, timestamp, note and outcome without modifying evidence or calculations.

## Scale

Columnar evidence supports paginated source queries, but the bounded analytical orchestrator materializes at most 100,000 records. Larger inputs fail explicitly. Million-record throughput requires streaming/SQL aggregation and measured benchmarks; readiness at that scale is not claimed.
