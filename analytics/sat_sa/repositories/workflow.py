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

    def jobs(self):
        with self._lock:
            return [json.loads(r[0]) for r in self._db().execute('SELECT payload FROM jobs ORDER BY job_id DESC LIMIT 100').fetchall()]

    def recover_jobs(self):
        for job in self.jobs():
            if job['status'] in ('queued','running'):
                self.save_job(job['job_id'],{**job,'status':'failed','error':'Application restarted before job completion; submit a new job'})

    def save_result(self,run_id,result):
        with self._lock:
            self._db().execute('INSERT INTO results VALUES (?,?)',[run_id,json.dumps(result)])

    def get_result(self,run_id):
        with self._lock:
            row=self._db().execute('SELECT payload FROM results WHERE run_id=?',[run_id]).fetchone()
            return json.loads(row[0]) if row else None

    def runs(self):
        with self._lock:
            rows=self._db().execute('SELECT payload FROM results ORDER BY run_id DESC LIMIT 100').fetchall()
            return [json.loads(r[0])['run'] for r in rows if 'run' in json.loads(r[0])]

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

    def decisions(self):
        with self._lock:
            return [json.loads(r[0]) for r in self._db().execute('SELECT payload FROM review_decisions ORDER BY decision_id LIMIT 1000').fetchall()]
