"""Supervisory endpoints with server-owned identities and paginated evidence."""
from datetime import datetime,timezone
import secrets
from typing import Literal
from uuid import uuid4
from fastapi import APIRouter,Depends,HTTPException,Query,Request
from sat_sa_contracts.models import PageResult,JobResult,Submission,RunRequest,ReviewInput
from sat_sa.ingestion.service import preview_submission
from sat_sa.ingestion.internal import fetch_export
from sat_sa.repositories.parquet_evidence import ParquetEvidenceRepository
from sat_sa.risk.overview import summarize

def router(settings):
    api=APIRouter(prefix='/api/v1')
    def identity(request:Request):
        token=request.headers.get('authorization','').removeprefix('Bearer ')
        for key,person in settings.auth_tokens.items():
            if secrets.compare_digest(token,key) and person.get('role') in ('reader','examiner','administrator') and person.get('actor'): return person
        if settings.demo_mode and not settings.auth_tokens: return {'actor':'local-demo-'+settings.demo_role,'role':settings.demo_role}
        raise HTTPException(401,'Valid configured bearer identity required')
    def writer(person=Depends(identity)):
        if person['role'] not in ('examiner','administrator'): raise HTTPException(403,'Examiner permission required')
        return person
    def result(request,run_id):
        runs=request.app.state.repository.runs(limit=1)
        selected=run_id or (runs[0]['run_id'] if runs else None)
        value=request.app.state.repository.get_result(selected) if selected else None
        if not value: raise HTTPException(404,'No completed analytics run; run analytics first')
        return value
    def page(items,offset,limit): return {'items':items[offset:offset+limit],'total':len(items),'offset':offset,'limit':limit}
    def bounds(limit:int=Query(50,ge=1,le=100),offset:int=Query(0,ge=0)): return offset,limit

    @api.get('/identity')
    def who(person=Depends(identity)): return person

    @api.get('/overview')
    def overview(request:Request,run_id:str|None=None,sector:str|None=None,person=Depends(identity)):
        return summarize(result(request,run_id),sector)

    @api.get('/datasets',response_model=PageResult)
    def datasets(request:Request,p=Depends(bounds),person=Depends(identity)): return page(request.app.state.repository.datasets(),*p)

    @api.post('/ingestion/preview')
    def preview(body:Submission,person=Depends(writer)):
        try: return preview_submission(body.model_dump())
        except (ValueError,TypeError,KeyError) as exc: raise HTTPException(422,str(exc)) from None

    @api.post('/ingestion',response_model=JobResult,status_code=202)
    def ingest(body:Submission,request:Request,person=Depends(writer)):
        try:
            checked=preview_submission(body.model_dump())
            if not checked['valid']: raise HTTPException(422,checked)
            if request.app.state.repository.get_dataset(body.dataset_id): raise HTTPException(409,'Dataset already registered')
            return request.app.state.workflow.submit('ingestion',body.dataset_id,person,body.model_dump())
        except ValueError as exc: raise HTTPException(422,str(exc)) from None

    @api.post('/analytics/run',response_model=JobResult,status_code=202)
    def run(body:RunRequest,request:Request,person=Depends(writer)):
        if not request.app.state.repository.get_dataset(body.dataset_id): raise HTTPException(404,'Dataset not registered')
        if len(request.app.state.repository.jobs(active_only=True))>=4: raise HTTPException(429,'Job queue is full')
        return request.app.state.workflow.submit('analytics',body.dataset_id,person)

    @api.post('/ingestion/internal',response_model=JobResult,status_code=202)
    def internal(body:RunRequest,request:Request,person=Depends(writer)):
        if person['role']!='administrator': raise HTTPException(403,'Administrator permission required for internal export')
        try: submission=Submission.model_validate({'dataset_id':body.dataset_id,**fetch_export(settings.internal_export_url)})
        except ValueError as exc: raise HTTPException(422,str(exc)) from None
        return ingest(submission,request,person)

    @api.get('/jobs/{job_id}',response_model=JobResult)
    def job(job_id:str,request:Request,person=Depends(identity)):
        found=request.app.state.repository.get_job(job_id)
        if not found: raise HTTPException(404,'Job not found')
        return found

    @api.get('/analytics/runs',response_model=PageResult)
    def runs(request:Request,p=Depends(bounds),person=Depends(identity)):
        repo=request.app.state.repository
        return {'items':repo.runs(limit=p[1],offset=p[0]),'total':repo.count_rows('results'),'offset':p[0],'limit':p[1]}

    @api.get('/entities',response_model=PageResult)
    def entities(request:Request,run_id:str|None=None,sector:str|None=None,peer_group:str|None=None,p=Depends(bounds),person=Depends(identity)):
        rows=result(request,run_id)['entities']
        return page([r for r in rows if (not sector or r['sector']==sector) and (not peer_group or r['peer_group']==peer_group)],*p)

    @api.get('/entities/{cse_id}')
    def entity(cse_id:str,request:Request,run_id:str|None=None,person=Depends(identity)):
        data=result(request,run_id); rows=[r for r in data['entities'] if r['cse_id']==cse_id]
        if not rows: raise HTTPException(404,'Entity not found')
        return {**rows[0],'unavailable':[u for u in data['unavailable'] if u['cse_id']==cse_id]}

    @api.get('/signals',response_model=PageResult)
    def signals(request:Request,run_id:str|None=None,cse_id:str|None=None,category:str|None=None,severity:str|None=None,expectation_only:bool=False,p=Depends(bounds),person=Depends(identity)):
        rows=[{k:v for k,v in s.items() if k not in ('evidence_references','thresholds')} for s in result(request,run_id)['signals'] if (not cse_id or s['cse_id']==cse_id) and (not category or s['category']==category) and (not severity or s['severity']==severity) and (not expectation_only or s['expectation'] is not None)]
        return page(rows,*p)

    @api.get('/signals/{signal_id}')
    def signal(signal_id:str,request:Request,run_id:str|None=None,p=Depends(bounds),person=Depends(identity)):
        rows=[s for s in result(request,run_id)['signals'] if s['signal_id']==signal_id]
        if not rows: raise HTTPException(404,'Signal not found')
        s=rows[0]; return {**s,'evidence_references':s['evidence_references'][p[0]:p[0]+p[1]]}

    @api.get('/review-queue',response_model=PageResult)
    def queue(request:Request,run_id:str|None=None,cse_id:str|None=None,min_priority:int=0,p=Depends(bounds),person=Depends(identity)):
        return page([q for q in result(request,run_id)['queue'] if (not cse_id or q['cse_id']==cse_id) and q['priority']>=min_priority],*p)

    @api.get('/evidence',response_model=PageResult)
    def evidence(request:Request,dataset_id:str,cse_id:str,table:Literal['cses','assets','alerts','cases','investigation_events','escalations'],record_id:str|None=None,p=Depends(bounds),person=Depends(identity)):
        repo=ParquetEvidenceRepository(settings.storage_root/'evidence'); registered=request.app.state.repository.get_dataset(dataset_id)
        if not registered: raise HTTPException(404,'Dataset not registered')
        try:
            manifest=repo.load_manifest(dataset_id)
            if manifest.dataset_hash!=registered.dataset_hash: raise ValueError('Immutable registration mismatch')
            rows,total=repo.query_records(dataset_id,table,cse_id,record_id=record_id,limit=p[1],offset=p[0])
            return {'items':[r.model_dump(mode='json') for r in rows],'total':total,'offset':p[0],'limit':p[1]}
        except (ValueError,OSError) as exc: raise HTTPException(422,str(exc)) from None

    @api.get('/trends',response_model=PageResult)
    def trends(request:Request,run_id:str|None=None,cse_id:str|None=None,p=Depends(bounds),person=Depends(identity)):
        return page([r for r in result(request,run_id)['trends'] if not cse_id or r['cse_id']==cse_id],*p)

    @api.get('/peer-analysis',response_model=PageResult)
    def peers(request:Request,run_id:str|None=None,p=Depends(bounds),person=Depends(identity)):
        return page([{'cse_id':r['cse_id'],**r['peer']} for r in result(request,run_id)['entities']],*p)

    @api.get('/validation')
    def validation(request:Request,run_id:str|None=None,person=Depends(identity)):
        data=result(request,run_id); reviews=request.app.state.repository.decisions(run_id=data['run']['run_id'])
        latest={}
        for r in sorted(reviews,key=lambda r:r['timestamp']): latest[r['signal_id']]=r
        final=[r for r in latest.values() if r['outcome'] in ('confirmed_concern','false_positive','explained')]
        return {'synthetic':data['validation'],'unavailable_reason':None if data['validation'] else 'No separate labels supplied for this dataset',
                'human_review':{'count':len(reviews),'unique_reviewed_signals':len(latest),'adjudicated_signals':len(final),
                'confirmed_yield':sum(r['outcome']=='confirmed_concern' for r in final)/len(final) if final else None,
                'recall':None,'limitation':'Only latest outcomes on reviewed signals; unreviewed population has no human labels',
                'outcomes':{outcome:sum(r['outcome']==outcome for r in latest.values()) for outcome in sorted({r['outcome'] for r in latest.values()})}}}

    @api.post('/reviews',status_code=201)
    def review(body:ReviewInput,request:Request,person=Depends(writer)):
        data=result(request,body.run_id)
        if not any(s['signal_id']==body.signal_id and s['cse_id']==body.cse_id for s in data['signals']): raise HTTPException(422,'Signal/entity/run reference does not match')
        decision={'decision_id':uuid4().hex,'signal_id':body.signal_id,'cse_id':body.cse_id,'timestamp':datetime.now(timezone.utc).isoformat(),**person,'outcome':body.outcome,'note':body.note}
        request.app.state.repository.record_decision(decision,body.run_id)
        return decision

    @api.get('/reviews',response_model=PageResult)
    def reviews(request:Request,p=Depends(bounds),person=Depends(identity)):
        repo=request.app.state.repository
        return {'items':repo.decisions(limit=p[1],offset=p[0]),'total':repo.count_rows('review_decisions'),'offset':p[0],'limit':p[1]}

    @api.get('/audit',response_model=PageResult)
    def audit(request:Request,p=Depends(bounds),person=Depends(identity)):
        repo=request.app.state.repository
        return {'items':[r.model_dump(mode='json') for r in repo.list_audit(limit=p[1],offset=p[0])],'total':repo.audit_count(),'offset':p[0],'limit':p[1]}
    return api
