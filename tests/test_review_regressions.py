import json
import pytest
from pathlib import Path
from sat_sa.repositories.workflow import WorkflowRepository
from sat_sa.ingestion.service import preview_submission
from sat_sa.synthetic.generator import build_records
from sat_sa.signals.engine import analyse

def test_recover_jobs_older_than_ui_page(tmp_path):
    with WorkflowRepository(tmp_path/'m.duckdb') as repo:
        repo.initialize();repo.save_job('000-pending',{'status':'running','kind':'analytics'})
        for i in range(101):repo.save_job(f'z{i:03}',{'status':'completed','kind':'analytics'})
        repo.recover_jobs()
        assert repo.get_job('000-pending')['status']=='failed'

def test_review_history_not_silently_truncated(tmp_path):
    with WorkflowRepository(tmp_path/'m.duckdb') as repo:
        repo.initialize()
        for i in range(1001):
            repo.record_decision({'decision_id':f'd{i:04}','signal_id':'s','cse_id':'C','actor':'human','role':'examiner','timestamp':'2026-09-27T00:00:00Z','outcome':'explained'},'run')
        assert len(repo.decisions())==1001

def test_long_csv_field_is_validation_error():
    with pytest.raises(ValueError):
        preview_submission({'files':[{'table':'cses','filename':'c.csv','content':'cse_id\n'+('x'*140000),'mapping':{}}]})

def test_escalation_denominator_only_eligible_records():
    records,_=build_records(20260927)
    cse=records['cses'][0]
    original=next(a for a in records['alerts'] if a.cse_id==cse.cse_id and a.closure_timestamp)
    missing=original.model_copy(update={'alert_id':'required','severity':'critical','escalation_required':True,'escalation_timestamp':None})
    ineligible=[original.model_copy(update={'alert_id':f'low{i}','severity':'low','escalation_required':False,'escalation_timestamp':None}) for i in range(99)]
    data={k:[] for k in records};data.update(cses=[cse],alerts=[missing,*ineligible])
    signal=next(s for s in analyse(data)['signals'] if s['rule_id']=='missing_escalation')
    assert signal['calculation']['denominator']==1
    assert signal['expectation']['observed']==0
    assert signal['confidence']=='limited'

def test_peers_require_matching_assessment_window():
    from datetime import datetime,timedelta,timezone
    from sat_sa_contracts.models import CSE,Alert,AssessmentPeriod
    start=datetime(2025,1,1,tzinfo=timezone.utc)
    p={'source_file':'test.json','source_record':'1','ingestion_batch':'test','transformation_version':'1'}
    data={k:[] for k in ('cses','alerts','cases','assets','investigation_events','escalations')}
    for index,days in enumerate([31,365,365,365]):
        cid=f'C{index}'
        data['cses'].append(CSE(cse_id=cid,name=cid,sector='energy',peer_group='p',criticality='critical',assessment_period=AssessmentPeriod(start=start,end=start+timedelta(days=days)),provenance=p))
        data['alerts'].extend(Alert(cse_id=cid,alert_id=f'A{i}',timestamp=start+timedelta(days=i),severity='low',source='test',alert_category='network',rule_use_case='test',provenance=p) for i in range(days))
    result=analyse(data)
    assert not any(s['rule_id']=='low_activity' and s['cse_id']=='C0' for s in result['signals'])
    assert any(u['cse_id']=='C0' and u['rule']=='peer_comparison' for u in result['unavailable'])

def test_missing_investigation_cannot_claim_complete_evidence():
    records,_=build_records(20260927)
    records['investigation_events']=[]
    result=analyse(records)
    signal=next(s for s in result['signals'] if s['rule_id']=='weak_investigation')
    assert signal['data_completeness']==0
    assert signal['confidence']=='limited'
    assert signal['completeness_basis']
