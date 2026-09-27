# Phase 1 boundaries and configuration

No analytics execute in Phase 1. No scores, signals, review rankings or validation performance results exist. Analytics packages establish import boundaries only.

`config/defaults.json` reserves versioned prototype defaults for later phases: 15-minute rapid closure, 30-day recurrence window, 20-record minimum sample, at least 3 peer entities, high/critical escalation expectations and critical-asset monitoring expectations. These are documented demonstration parameters, not NCIIPC policy, calibrated thresholds or compliance rules. Severity mapping maps numeric levels 1–5 to critical–informational; later ingestion must explicitly select a source mapping.

The dataset generator injects scenarios from `analytics/sat_sa/synthetic/scenarios.py`. Energy and financial-services cohorts each contain four medium critical entities. There are 24 inventory assets per entity, including 8 critical assets. The ordinary workload is ten cases per month with eight linked alerts per case. The low-activity entity has one case per month. This is controlled synthetic data for integration and later validation; its patterns are deliberately simplified, not an empirical national SOC workload model.

The healthy control has complete investigation and expected escalation evidence. Future analytics must use sufficient cohorts, distinguish missingness from misconduct and explain their observations; labels must never become an analytics input.
