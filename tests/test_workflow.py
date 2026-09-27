from pathlib import Path
import pytest
from sat_sa.repositories.workflow import WorkflowRepository
from sat_sa.validation.evaluate import evaluate

def test_job_and_review_restart(tmp_path):
    path=tmp_path/'metadata.duckdb'
    with WorkflowRepository(path) as repo:
        repo.initialize()
        repo.save_job('j1',{'status':'running','kind':'analytics'})
        repo.save_result('run-1',{'dataset_id':'demo','signals':[]})
        repo.record_decision({'decision_id':'d1','signal_id':'s1','cse_id':'CSE-01','actor':'examiner','role':'examiner',
             'timestamp':'2026-09-27T00:00:00Z','outcome':'explained','note':'Checked'},'run-1')
    with WorkflowRepository(path) as repo:
        repo.initialize(); repo.recover_jobs()
        assert repo.get_job('j1')['status']=='failed'
        assert repo.get_result('run-1')['dataset_id']=='demo'
        assert repo.decisions()[0]['outcome']=='explained'
        assert repo.list_audit()[-1].action=='review_recorded'

def test_validation_denominators_and_empty():
    records={'alerts':[],'cases':[],'assets':[],'cses':[],'investigation_events':[],'escalations':[]}
    result=evaluate([],[],[],records)
    assert result['precision'] is None and result['recall'] is None
    assert result['universe']==0
