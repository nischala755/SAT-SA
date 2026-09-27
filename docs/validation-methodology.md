# Validation methodology

Labels are read only after analytics and ranking complete. They cannot influence rules and are never returned through evidence APIs. Human-review outcomes remain separate.

## Synthetic labelled universe

Universe: all entity-scoped records across six normalized tables. Positive: referenced by an injected scenario other than healthy_control. Other records count as negatives **only for this benchmark**. Predicted positive: referenced by at least one signal. This evaluates sample selection, not per-scenario classification; the broad universe and simplified generator affect results.

| Metric | Definition |
| --- | --- |
| Precision | Selected labelled positives / selected records |
| Recall | Selected labelled positives / labelled positives |
| False-positive rate | Selected unlabelled records / all unlabelled records |
| Coverage | Selected records / universe |
| Precision@20 | Labelled positives in first min(20, queue size) / actual top-N |
| Recall@20 | Those positives / all labelled positives |
| Ranking quality | Average precision across queue / labelled positives; missed positives contribute zero |
| Traceability | References resolving to CSE/type/ID universe / all references |
| Random baseline | Up to 20 distinct universe records sampled with seed 20260927 |

Zero denominators return null. No measured review timings exist, so time savings are unavailable. Injections are not operational ground truth.

## Human-reviewed outcomes

Use the latest outcome for each signal/run. Confirmed concern, explained and false-positive outcomes form the adjudicated subset; pending, further-investigation and insufficient-evidence outcomes are excluded from confirmed yield. Recall is unavailable because unreviewed records lack human labels. Report event count and unique reviewed/adjudicated counts.

## Initial measured benchmark

Seed 20260927: 13,886 records, 1,361 labelled positives, 2,329 selected records, 1,301 true positives and 1,028 false positives. Initial measured precision 55.86%, recall 95.59%, false-positive rate 8.21%, Precision@20 100%, Recall@20 1.47%, random Precision@20 10%, average precision 88.13%, traceability 100%. Consult completion verification for final-version results; these values are not promised real-world effectiveness.

## Engineering verification

Tests cover validation, deterministic artifacts, CSE-scoped references, immutability, mapping, jobs, reviews, permissions and recovery. Predicate fixtures include positive and normal examples. Browser tests exercise actual status, outage/retry and overview→evidence→human decision→audit. Isolated-container verification checks denied external TCP and actual analytics/review operation. Optional AI verification is separate.
