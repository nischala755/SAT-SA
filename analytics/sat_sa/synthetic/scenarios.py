"""Generator scenario names and explicit intentions; never analytics results."""
SCENARIOS = {
    "fast_closure": "High-severity alerts close within fifteen minutes in the second half of the year.",
    "recurring_alerts": "Repeated alerts on one asset with absent remediation/root-cause evidence.",
    "missing_escalation": "Escalation expected but no escalation record supplied.",
    "missing_monitoring": "Critical inventory assets expect monitoring but have no submitted alerts.",
    "template_repetition": "Cases repeat one investigation action and identical closure wording.",
    "low_activity": "A critical environment has one tenth the monthly case and alert activity of its declared peers.",
    "peer_deviation": "Comparable cases have substantially longer closure durations than cohort peers.",
    "closure_bursts": "Multiple cases close at the same month-end timestamp.",
    "metric_evidence_mismatch": "Fast closure coincides with absent investigation and escalation evidence.",
    "healthy_control": "Control entity has complete, varied investigation and escalation evidence; no adverse injection.",
}
