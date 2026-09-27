"""Immutable local Parquet datasets. Labels are not an evidence table."""
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
from sat_sa_contracts.models import Artifact, DatasetManifest, RECORD_MODELS, RECORD_KEYS

from .relationships import validate_records


def canonical_json(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def arrow_type(schema, definitions):
    if "$ref" in schema:
        return arrow_type(definitions[schema["$ref"].split("/")[-1]], definitions)
    if "anyOf" in schema:
        return arrow_type(next(s for s in schema["anyOf"] if s.get("type") != "null"), definitions)
    kind = schema.get("type")
    if kind == "object":
        return pa.struct([pa.field(k, arrow_type(v, definitions)) for k, v in schema["properties"].items()])
    if kind == "string":
        return pa.timestamp("us", tz="UTC") if schema.get("format") == "date-time" else pa.string()
    return {"integer": pa.int64(), "number": pa.float64(), "boolean": pa.bool_()}[kind]


def schema_for(model):
    schema = model.model_json_schema()
    return pa.schema([pa.field(k, arrow_type(v, schema.get("$defs", {}))) for k, v in schema["properties"].items()])


class ParquetEvidenceRepository:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def _dataset_path(self, dataset_id: str) -> Path:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]*", dataset_id) or ":" in dataset_id:
            raise ValueError("Invalid dataset path identifier")
        target = (self.root / dataset_id).resolve()
        if target.parent != self.root:
            raise ValueError("Dataset must be directly within evidence root")
        return target

    def write_dataset(self, records: dict, destination: Path, *, seed: int | None, generator_version: str | None = '1.0.0') -> DatasetManifest:
        destination = destination.resolve()
        if destination != self._dataset_path(destination.name):
            raise ValueError("Destination outside evidence root")
        if destination.exists():
            raise FileExistsError("Dataset versions are immutable")
        records = validate_records(records)
        self.root.mkdir(parents=True, exist_ok=True)
        lock = self.root / f".{destination.name}.lock"
        with lock.open("x") as lock_handle:
            # File existence is the reservation; close before Windows cleanup.
            lock_handle.close()
            staging = Path(tempfile.mkdtemp(prefix=".staging-", dir=self.root))
            try:
                artifacts = []
                for kind, model in sorted(RECORD_MODELS.items()):
                    table = pa.Table.from_pylist([row.model_dump(mode="python") for row in records[kind]], schema=schema_for(model))
                    path = staging / f"{kind}.parquet"
                    pq.write_table(table, path, version="2.6", compression="NONE", use_dictionary=False, write_statistics=True, row_group_size=8192)
                    artifacts.append(Artifact(filename=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), row_count=table.num_rows))
                digest = hashlib.sha256(canonical_json([a.model_dump() for a in artifacts])).hexdigest()
                periods = [c.assessment_period for c in records["cses"]]
                manifest = DatasetManifest(dataset_id=destination.name, dataset_hash=digest, schema_version="1.0.0", generator_version=generator_version, seed=seed, created_at=max(p.end for p in periods), assessment_period={"start": min(p.start for p in periods), "end": max(p.end for p in periods)}, artifacts=tuple(artifacts))
                (staging / "manifest.json").write_bytes(canonical_json(manifest.model_dump(mode="json")))
                if destination.exists():
                    raise FileExistsError("Dataset versions are immutable")
                staging.rename(destination)
                return manifest
            finally:
                if staging.exists():
                    shutil.rmtree(staging)
                lock.unlink(missing_ok=True)

    def load_manifest(self, dataset_id: str, *, verify: bool = True) -> DatasetManifest:
        directory = self._dataset_path(dataset_id)
        manifest = DatasetManifest.model_validate_json((directory / "manifest.json").read_bytes())
        if manifest.dataset_id != dataset_id or {a.filename for a in manifest.artifacts} != {f"{k}.parquet" for k in RECORD_MODELS}:
            raise ValueError("Manifest does not match dataset layout")
        if verify:
            for a in manifest.artifacts:
                path = directory / a.filename
                if hashlib.sha256(path.read_bytes()).hexdigest() != a.sha256 or pq.read_metadata(path).num_rows != a.row_count:
                    raise ValueError(f"Artifact integrity failure: {a.filename}")
            digest = hashlib.sha256(canonical_json([a.model_dump() for a in manifest.artifacts])).hexdigest()
            if digest != manifest.dataset_hash:
                raise ValueError("Dataset hash does not match manifest")
        return manifest

    def read_records(self, dataset_id: str, record_type: str, cse_id: str, *, limit: int = 100, offset: int = 0) -> list:
        if record_type not in RECORD_MODELS:
            raise ValueError("Unknown evidence table")
        if not 1 <= limit <= 1000 or offset < 0:
            raise ValueError("Invalid pagination")
        path = self._dataset_path(dataset_id) / f"{record_type}.parquet"
        # The path is local and selected exclusively from the evidence allowlist.
        with duckdb.connect(config={"autoinstall_known_extensions": "false", "autoload_known_extensions": "false"}) as con:
            result = con.execute(f'SELECT * FROM read_parquet(?) WHERE cse_id = ? ORDER BY "{RECORD_KEYS[record_type]}" LIMIT ? OFFSET ?', [str(path), cse_id, limit, offset])
            names = [col[0] for col in result.description]
            return [RECORD_MODELS[record_type].model_validate(dict(zip(names, row))) for row in result.fetchall()]

    def query_records(self,dataset_id,record_type,cse_id,*,record_id=None,limit=50,offset=0):
        if record_type not in RECORD_MODELS or not 1<=limit<=100 or offset<0: raise ValueError('Invalid evidence query')
        path=self._dataset_path(dataset_id)/f'{record_type}.parquet'
        key=RECORD_KEYS[record_type]
        predicate='cse_id = ?'; params=[str(path),cse_id]
        if record_id is not None:
            predicate+=f' AND "{key}" = ?'; params.append(record_id)
        with duckdb.connect(config={'autoinstall_known_extensions':'false','autoload_known_extensions':'false'}) as con:
            total=con.execute(f'SELECT COUNT(*) FROM read_parquet(?) WHERE {predicate}',params).fetchone()[0]
            cursor=con.execute(f'SELECT * FROM read_parquet(?) WHERE {predicate} ORDER BY "{key}" LIMIT ? OFFSET ?',params+[limit,offset])
            names=[c[0] for c in cursor.description]
            return [RECORD_MODELS[record_type].model_validate(dict(zip(names,row))) for row in cursor.fetchall()],total
