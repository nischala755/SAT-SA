# Phase 1 validation scope

Phase 1 verifies model validation, configuration, immutable storage, audit atomicity, deterministic generation, contracts and application connectivity. It does not measure precision, recall, ranking quality or time saved because no analytical engine exists yet.

Generator tests compare every evidence and label artifact hash and every Parquet logical row for equal seeds with the same logical dataset name. A different seed must change the evidence hash. Tests also check composite foreign keys, real injected fast closure/missing escalation/monitoring gaps, twelve months, minimum scale and healthy-control escalation completeness.

Persistence checks close/reopen the database in process and in a new Python process; runtime verification also restarts application processes and Compose services. Duplicate registration is an error even for an identical version, and registration plus its audit event is atomic.

The checked-in verification report distinguishes actual test results from unavailable checks. No synthetic labels are presented as analytical results.
