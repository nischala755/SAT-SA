from sat_sa.risk.period_comparison import compare_runs


def run(run_id, start, end, entities):
    return {
        'run': {'run_id': run_id, 'dataset_id': run_id, 'dataset_hash': run_id + '-hash',
                'assessment_period': {'start': start, 'end': end}},
        'entities': entities,
    }


def entity(cse_id='CSE-01', alerts=30, cases=15, completeness=.9, high_priority=2):
    return {'cse_id': cse_id, 'name': cse_id, 'sector': 'energy',
            'peer_group': 'energy-critical', 'alerts': alerts, 'cases': cases,
            'completeness': completeness, 'high_priority': high_priority}


def test_period_comparison_normalizes_by_days_and_keeps_provenance():
    baseline = run('before', '2024-01-01T00:00:00Z', '2024-01-31T00:00:00Z', [entity()])
    current = run('after', '2025-01-01T00:00:00Z', '2025-03-02T00:00:00Z', [entity(alerts=60, cases=30)])
    result = compare_runs(baseline, current)
    row = result['entities'][0]
    assert row['comparable'] is True
    assert row['baseline']['alerts_per_30_days'] == row['current']['alerts_per_30_days'] == 30
    assert row['alert_rate_change_per_30_days'] == 0
    assert result['baseline']['dataset_hash'] == 'before-hash'
    assert result['current']['run_id'] == 'after'


def test_period_comparison_marks_missing_and_changed_cohorts_unavailable():
    baseline = run('before', '2024-01-01T00:00:00Z', '2024-02-01T00:00:00Z', [entity(), entity('CSE-02')])
    changed = entity()
    changed['peer_group'] = 'different'
    current = run('after', '2025-01-01T00:00:00Z', '2025-02-01T00:00:00Z', [changed, entity('CSE-03')])
    rows = {r['cse_id']: r for r in compare_runs(baseline, current)['entities']}
    assert not rows['CSE-01']['comparable'] and rows['CSE-01']['alert_rate_change_per_30_days'] is None
    assert not rows['CSE-02']['comparable'] and not rows['CSE-03']['comparable']


def test_reused_identifier_with_different_entity_name_is_not_compared():
    baseline = run('before', '2024-01-01T00:00:00Z', '2024-02-01T00:00:00Z', [entity()])
    replacement = entity()
    replacement['name'] = 'Different entity with recycled local ID'
    current = run('after', '2025-01-01T00:00:00Z', '2025-02-01T00:00:00Z', [replacement])
    row = compare_runs(baseline, current)['entities'][0]
    assert row['comparable'] is False
    assert row['alert_rate_change_per_30_days'] is None


def test_period_comparison_rejects_overlap_or_reversed_order():
    import pytest
    baseline = run('before', '2025-01-01T00:00:00Z', '2025-03-01T00:00:00Z', [entity()])
    current = run('after', '2025-02-01T00:00:00Z', '2025-04-01T00:00:00Z', [entity()])
    with pytest.raises(ValueError, match='non-overlapping'):
        compare_runs(baseline, current)
