"""Single-process metadata owner; transactions serialize through one connection."""
from datetime import datetime, timezone
import hashlib
from pathlib import Path
from threading import RLock

import duckdb
from sat_sa_contracts.models import AuditEvent, DatasetVersion


class DuplicateDatasetError(ValueError):
    pass


class DuckDBMetadataRepository:
    def __init__(self, path: Path):
        self.path = Path(path)
        self._connection = None
        self._lock = RLock()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def initialize(self) -> None:
        with self._lock:
            if self._connection is not None:
                return
            self.path.parent.mkdir(parents=True, exist_ok=True)
            con = duckdb.connect(str(self.path), config={"enable_external_access": "false", "autoinstall_known_extensions": "false", "autoload_known_extensions": "false"})
            try:
                con.execute("CREATE TABLE IF NOT EXISTS datasets (dataset_id VARCHAR PRIMARY KEY, payload VARCHAR NOT NULL)")
                con.execute("CREATE SEQUENCE IF NOT EXISTS audit_sequence START 1")
                con.execute("CREATE TABLE IF NOT EXISTS audit (sequence BIGINT DEFAULT nextval('audit_sequence'), event_id VARCHAR PRIMARY KEY, payload VARCHAR NOT NULL)")
                con.execute("CREATE TABLE IF NOT EXISTS analytics_runs (run_id VARCHAR PRIMARY KEY, dataset_id VARCHAR NOT NULL REFERENCES datasets(dataset_id), payload VARCHAR NOT NULL)")
                con.execute("CREATE TABLE IF NOT EXISTS review_decisions (decision_id VARCHAR PRIMARY KEY, payload VARCHAR NOT NULL)")
            except Exception:
                con.close()
                raise
            self._connection = con

    def _db(self):
        if self._connection is None:
            raise RuntimeError("Metadata storage is not initialized")
        return self._connection

    def register_dataset(self, dataset: DatasetVersion) -> None:
        # Revalidation blocks callers bypassing Pydantic with model_construct/copy.
        dataset = DatasetVersion.model_validate_json(dataset.model_dump_json())
        with self._lock:
            con = self._db()
            if self.get_dataset(dataset.dataset_id) is not None:
                raise DuplicateDatasetError(f"Dataset version already exists: {dataset.dataset_id}")
            event_id = f"register:{dataset.dataset_id}"
            if len(event_id) > 160:
                event_id = "register-sha256:" + hashlib.sha256(dataset.dataset_id.encode()).hexdigest()
            event = AuditEvent(event_id=event_id, timestamp=datetime.now(timezone.utc), actor="local-demo-bootstrap", role="administrator", action="dataset_registered", object_id=dataset.dataset_id, details={"dataset_hash": dataset.dataset_hash})
            con.execute("BEGIN TRANSACTION")
            try:
                con.execute("INSERT INTO datasets VALUES (?, ?)", [dataset.dataset_id, dataset.model_dump_json()])
                self.append_audit(event)
                con.execute("COMMIT")
            except Exception:
                con.execute("ROLLBACK")
                raise

    def get_dataset(self, dataset_id: str) -> DatasetVersion | None:
        with self._lock:
            row = self._db().execute("SELECT payload FROM datasets WHERE dataset_id = ?", [dataset_id]).fetchone()
            return DatasetVersion.model_validate_json(row[0]) if row else None

    def append_audit(self, event: AuditEvent) -> None:
        event = AuditEvent.model_validate_json(event.model_dump_json())
        with self._lock:
            self._db().execute("INSERT INTO audit (event_id, payload) VALUES (?, ?)", [event.event_id, event.model_dump_json()])

    def list_audit(self, limit: int = 100, offset: int = 0) -> list[AuditEvent]:
        if not 1 <= limit <= 1000 or offset < 0:
            raise ValueError("Invalid pagination")
        with self._lock:
            rows = self._db().execute("SELECT payload FROM audit ORDER BY sequence LIMIT ? OFFSET ?", [limit, offset]).fetchall()
            return [AuditEvent.model_validate_json(row[0]) for row in rows]

    def status(self) -> dict:
        with self._lock:
            count = self._db().execute("SELECT COUNT(*) FROM datasets").fetchone()[0]
            self._db().execute("SELECT COUNT(*) FROM audit").fetchone()
            return {"storage_ready": True, "registered_datasets": count}

    def close(self) -> None:
        with self._lock:
            if self._connection is not None:
                self._connection.close()
                self._connection = None
