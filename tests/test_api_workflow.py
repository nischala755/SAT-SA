import time
from pathlib import Path
from fastapi.testclient import TestClient
from sat_sa_api.main import create_app
from sat_sa.config.settings import Settings
from sat_sa.synthetic.bootstrap import ensure_demo

def test_real_run_review_audit_and_reader(tmp_path):
    settings=Settings(storage_root=tmp_path)
    ensure_demo(settings)
    with TestClient(create_app(settings)) as client:
        response=client.post('/api/v1/analytics/run',json={'dataset_id':'demo'})
        assert response.status_code==202
        job=response.json()
        for _ in range(300):
            job=client.get('/api/v1/jobs/'+job['job_id']).json()
            if job['status'] in ('completed','failed'): break
            time.sleep(.05)
        assert job['status']=='completed',job
        run=job['run_id']
        report=client.get('/api/v1/reports/'+run)
        assert report.status_code==200
        assert report.json()['run']['run_id']==run
        assert report.json()['status']=='requires_human_review'
        assert client.get('/api/v1/period-comparison',params={'baseline_run_id':run,'current_run_id':run}).status_code==422
        signals=client.get('/api/v1/signals',params={'run_id':run}).json()
        assert signals['total']>0
        signal=signals['items'][0]
        payload={'run_id':run,'signal_id':signal['signal_id'],'cse_id':signal['cse_id'],'outcome':'explained','note':'Human checked source context'}
        assert client.post('/api/v1/reviews',json=payload).status_code==201
        assert client.post('/api/v1/reviews',json={**payload,'cse_id':'OTHER'}).status_code==422
        assert client.get('/api/v1/audit').json()['total']>=3
        assert client.get('/api/v1/evidence',params={'dataset_id':'demo','cse_id':'CSE-01','table':'labels'}).status_code==422
    with TestClient(create_app(Settings(storage_root=tmp_path,demo_role='reader'))) as client:
        assert client.post('/api/v1/reviews',json=payload,headers={'X-Role':'administrator'}).status_code==403
        assert client.get('/api/v1/reviews').json()['total']==1

def test_production_auth_and_spoof(tmp_path):
    settings=Settings(storage_root=tmp_path,demo_mode=False,auth_tokens={'reader-secret':{'actor':'alice','role':'reader'}})
    with TestClient(create_app(settings)) as client:
        assert client.get('/api/v1/entities').status_code==401
        assert client.post('/api/v1/analytics/run',json={'dataset_id':'demo'},headers={'Authorization':'Bearer reader-secret','X-Role':'administrator'}).status_code==403

def test_import_preview_commit_and_duplicate(tmp_path):
    import json
    from sat_sa.repositories.parquet_evidence import ParquetEvidenceRepository
    record=ParquetEvidenceRepository(Path('data/sample')).read_records('demo','cses','CSE-01')[0].model_dump(mode='json')
    body={'dataset_id':'uploaded','files':[{'table':'cses','filename':'cses.json','content':json.dumps([record]),'mapping':{}}]}
    with TestClient(create_app(Settings(storage_root=tmp_path))) as client:
        assert client.post('/api/v1/ingestion/preview',json=body).json()['valid']
        response=client.post('/api/v1/ingestion',json=body)
        assert response.status_code==202
        job=response.json()
        for _ in range(100):
            job=client.get('/api/v1/jobs/'+job['job_id']).json()
            if job['status'] in ('completed','failed'): break
            time.sleep(.03)
        assert job['status']=='completed',job
        assert client.post('/api/v1/ingestion',json=body).status_code==409
        evidence=client.get('/api/v1/evidence',params={'dataset_id':'uploaded','cse_id':'CSE-01','table':'cses'}).json()
        assert evidence['items'][0]['provenance']['source_record']=='1'
        assert evidence['items'][0]['provenance']['ingestion_batch']=='uploaded'
        assert client.get('/api/v1/ingestion/internal').status_code==405
        assert list((tmp_path/'raw').glob('*/submission.json'))
