from copy import deepcopy
import pytest
from sat_sa.synthetic.generator import build_records
from sat_sa.signals.engine import analyse
from sat_sa.peer_analysis.statistics import peer_stats
from sat_sa.prioritization.queue import prioritize

@pytest.fixture(scope='module')
def records(): return build_records(20260927)[0]

def test_reproducible_and_evidence_scoped(records):
    a=analyse(records); b=analyse(records)
    assert a==b and a['signals']
    assert {s['category'] for s in a['signals']}=={'detection','investigation','escalation','incident_response','security_operations','governance','operational_discipline','cyber_resilience'}
    for s in a['signals']:
        assert s['observed_evidence'] and s['methodology'] and s['calculation']
        assert all(r['cse_id']==s['cse_id'] for r in s['evidence_references'])

def test_fast_positive_normal_negative(records):
    results=analyse(records)['signals']
    assert any(s['rule_id']=='fast_closure' and s['cse_id']=='CSE-01' for s in results)
    assert not any(s['rule_id']=='fast_closure' and s['cse_id']=='CSE-04' for s in results)

def test_missing_inventory_suppresses_coverage(records):
    data={**records,'assets':[]}
    result=analyse(data)
    assert not any(s['rule_id']=='monitoring_gap' for s in result['signals'])
    assert any('inventory' in x['reason'] for x in result['unavailable'])

def test_peer_excludes_subject():
    assert peer_stats(100,[1,2,3],3)['median']==2
    assert peer_stats(100,[1,2],3)['available'] is False

def test_queue_deduplicates_and_explains(records):
    result=analyse(records); queue=prioritize(result['signals'])
    keys=[(q['cse_id'],q['record_type'],q['record_id']) for q in queue]
    assert len(keys)==len(set(keys))
    assert all(abs(q['priority']-sum(q['contributions'].values()))<1e-6 for q in queue)
