from sat_sa.risk.report import build_report


def test_report_only_uses_stored_evidence_and_human_decisions():
    result = {
        'run': {'run_id': 'r1', 'dataset_id': 'd1', 'dataset_hash': 'sha', 'configuration_hash': 'cfg',
                'assessment_period': {'start': '2025-01-01', 'end': '2025-12-31'}},
        'entities': [{'cse_id': 'C1', 'name': 'Entity 1', 'sector': 'energy', 'alerts': 12,
                      'cases': 3, 'high_priority': 1, 'completeness': .75}],
        'signals': [{'signal_id': 's1', 'cse_id': 'C1', 'name': 'Expected escalation evidence absent',
                     'category': 'escalation', 'confidence': 'limited', 'evidence_count': 2,
                     'observed_evidence': '2 of 5 match', 'methodology': 'Documented rule',
                     'expectation': {'expected': 5, 'observed': 3, 'gap': 2, 'source': 'configured rule'},
                     'evidence_references': [{'record_id': 'a1', 'record_type': 'alerts', 'cse_id': 'C1'}]}],
        'queue': [{'cse_id': 'C1', 'record_id': 'a1', 'record_type': 'alerts', 'priority': 10,
                   'reasons': ['s1']}], 'unavailable': [], 'trends': [],
    }
    report = build_report(result, [])
    assert report['status'] == 'requires_human_review'
    assert report['review_decisions'] == []
    assert report['signals'][0]['evidence_references'][0]['record_id'] == 'a1'
    assert report['signals'][0]['expectation']['gap'] == 2
    assert report['run']['dataset_hash'] == 'sha'
    assert 'ground_truth' not in str(report)
    assert build_report(result, [{'signal_id': 's1', 'outcome': 'explained', 'note': 'Checked'}])['review_decisions'][0]['outcome'] == 'explained'
