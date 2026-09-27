"""Single local worker, persisted states, immutable results."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import hashlib
import json
from time import monotonic
from uuid import uuid4
from sat_sa.repositories.datasets import load_dataset
from sat_sa.repositories.parquet_evidence import ParquetEvidenceRepository,canonical_json
from sat_sa.ingestion.service import normalize_submission
from sat_sa.signals.engine import analyse,VERSION
from sat_sa.prioritization.queue import prioritize
from sat_sa.validation.evaluate import evaluate

class Workflow:
    def __init__(self,repository,settings):
        self.repo=repository; self.settings=settings
        self.executor=ThreadPoolExecutor(max_workers=1,thread_name_prefix='sat-sa-jobs')

    def submit(self,kind,dataset_id,identity,submission=None):
        job={'job_id':uuid4().hex,'kind':kind,'dataset_id':dataset_id,'status':'queued','error':None,'run_id':None}
        self.repo.save_job(job['job_id'],job)
        self.repo.event(identity['actor'],identity['role'],kind+'_queued',job['job_id'],{'dataset_id':dataset_id})
        self.executor.submit(self.execute,job,identity,submission)
        return job

    def execute(self,job,identity,submission):
        job={**job,'status':'running'}; self.repo.save_job(job['job_id'],job)
        try:
            root=self.settings.storage_root
            if job['kind']=='ingestion':
                if self.repo.get_dataset(job['dataset_id']): raise ValueError('Dataset version already registered')
                records=normalize_submission(submission,job['dataset_id'])
                raw=root/'raw'/job['job_id']; raw.mkdir(parents=True,exist_ok=False)
                payload=canonical_json(submission); (raw/'submission.json').write_bytes(payload)
                manifest=ParquetEvidenceRepository(root/'evidence').write_dataset(records,root/'evidence'/job['dataset_id'],seed=None,generator_version=None)
                self.repo.register_dataset(manifest)
                self.repo.event(identity['actor'],identity['role'],'ingestion_completed',job['dataset_id'],{'source_hash':hashlib.sha256(payload).hexdigest(),'job_id':job['job_id']})
            else:
                start=monotonic(); started=datetime.now(timezone.utc)
                registered=self.repo.get_dataset(job['dataset_id'])
                if not registered: raise ValueError('Dataset is not registered')
                manifest,records=load_dataset(root/'evidence',job['dataset_id'])
                if manifest.dataset_hash!=registered.dataset_hash: raise ValueError('Dataset differs from registration')
                result=analyse(records,dataset_id=job['dataset_id']); queue=prioritize(result['signals'])
                run_id=started.strftime('%Y%m%dT%H%M%S')+'-'+uuid4().hex[:12]
                run={'run_id':run_id,'dataset_id':manifest.dataset_id,'dataset_hash':manifest.dataset_hash,'analytics_version':VERSION,'software_version':'0.2.0',
                    'configuration':result['config'],'configuration_hash':result['configuration_hash'],'assessment_period':manifest.assessment_period.model_dump(mode='json'),
                    'started_at':started.isoformat(),'completed_at':datetime.now(timezone.utc).isoformat(),'status':'completed',
                    'records_analysed':sum(map(len,records.values())),'findings_generated':len(result['signals']),'execution_seconds':monotonic()-start}
                for s in result['signals']: s['run_id']=run_id
                validation=None
                labels=root/'ground_truth'/manifest.dataset_id/'labels.json'
                if self.settings.demo_mode and manifest.generator_version and labels.exists():
                    validation=evaluate(result['signals'],queue,json.loads(labels.read_text()),records)
                self.repo.save_result(run_id,{**result,'dataset_id':manifest.dataset_id,'run':run,'queue':queue,'validation':validation})
                self.repo.event(identity['actor'],identity['role'],'analytics_completed',run_id,{'dataset_hash':manifest.dataset_hash,'signals':len(result['signals'])})
                job['run_id']=run_id
            job['status']='completed'
        except Exception as exc:
            job.update(status='failed',error=str(exc)[:1000])
            self.repo.event(identity['actor'],identity['role'],job['kind']+'_failed',job['job_id'],{'error':type(exc).__name__})
        finally: self.repo.save_job(job['job_id'],job)

    def close(self): self.executor.shutdown(wait=True,cancel_futures=False)
