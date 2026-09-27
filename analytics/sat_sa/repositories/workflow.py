"""Persistent job/run/review boundary sharing the metadata owner's lock."""
from datetime import datetime,timezone
import json
from uuid import uuid4
from sat_sa_contracts.models import AuditEvent, ReviewDecision
from .duckdb_metadata import DuckDBMetadataRepository

class WorkflowRepository(DuckDBMetadataRepository):
    def initialize(self):
        super().initialize()
        with self._lock:
            for name,key in [('jobs','job_id'),('results','run_id')]:
                self._db().execute(f'CREATE TABLE IF NOT EXISTS {name} ({key} VARCHAR PRIMARY KEY, payload VARCHAR NOT NULL)')

    def datasets(self):
        with self._lock:
            return [json.loads(r[0]) for r in self._db().execute('SELECT payload FROM datasets ORDER BY dataset_id').fetchall()]

    def audit_count(self):
        with self._lock: return self._db().execute('SELECT count(*) FROM audit').fetchone()[0]

    def save_job(self,job_id,payload):
        with self._lock:
            self._db().execute('INSERT OR REPLACE INTO jobs VALUES (?,?)',[job_id,json.dumps({'job_id':job_id,**payload})])

    def get_job(self,job_id):
        with self._lock:
            row=self._db().execute('SELECT payload FROM jobs WHERE job_id=?',[job_id]).fetchone()
            return json.loads(row[0]) if row else None

    def jobs(self,active_only=False):
        with self._lock:
            where=" WHERE json_extract_string(payload, '$.status') IN ('queued','running')" if active_only else ''
            return [json.loads(r[0]) for r in self._db().execute('SELECT payload FROM jobs'+where+' ORDER BY job_id DESC').fetchall()]

    def recover_jobs(self):
        for job in self.jobs(active_only=True):
            if job['status'] in ('queued','running'):
                self.save_job(job['job_id'],{**job,'status':'failed','error':'Application restarted before job completion; submit a new job'})

    def save_result(self,run_id,result):
        with self._lock:
            self._db().execute('INSERT INTO results VALUES (?,?)',[run_id,json.dumps(result)])

    def get_result(self,run_id):
        with self._lock:
            row=self._db().execute('SELECT payload FROM results WHERE run_id=?',[run_id]).fetchone()
            return json.loads(row[0]) if row else None

    def runs(self,limit=None,offset=0):
        with self._lock:
            query='SELECT payload FROM results ORDER BY run_id DESC'
            rows=self._db().execute(query+(' LIMIT ? OFFSET ?' if limit is not None else ''),[limit,offset] if limit is not None else []).fetchall()
            return [json.loads(r[0])['run'] for r in rows if 'run' in json.loads(r[0])]

    def count_rows(self,table):
        if table not in ('results','review_decisions'): raise ValueError('Invalid metadata table')
        with self._lock: return self._db().execute(f'SELECT count(*) FROM {table}').fetchone()[0]

    def event(self,actor,role,action,object_id,details=None):
        self.append_audit(AuditEvent(event_id=uuid4().hex,timestamp=datetime.now(timezone.utc),actor=actor,
             role=role,action=action,object_id=object_id,details=details or {}))

    def record_decision(self,decision,run_id):
        validated=ReviewDecision.model_validate(decision)
        with self._lock:
            con=self._db(); con.execute('BEGIN TRANSACTION')
            try:
                con.execute('INSERT INTO review_decisions VALUES (?,?)',[validated.decision_id,json.dumps({**validated.model_dump(mode='json'),'run_id':run_id})])
                self.event(validated.actor,validated.role,'review_recorded',validated.decision_id,{'run_id':run_id,'signal_id':validated.signal_id,'outcome':validated.outcome})
                con.execute('COMMIT')
            except Exception:
                con.execute('ROLLBACK'); raise

    def decisions(self,limit=None,offset=0,run_id=None):
        with self._lock:
            query='SELECT payload FROM review_decisions'; params=[]
            if run_id is not None:
                query+=" WHERE json_extract_string(payload, '$.run_id') = ?";params.append(run_id)
            query+=" ORDER BY json_extract_string(payload, '$.timestamp'), decision_id"
            if limit is not None: query+=' LIMIT ? OFFSET ?';params.extend([limit,offset])
            return [json.loads(r[0]) for r in self._db().execute(query,params).fetchall()]
