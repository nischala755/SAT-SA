"""Verified local loading for bounded prototype jobs."""
import pyarrow.parquet as pq
from sat_sa_contracts.models import RECORD_MODELS
from .parquet_evidence import ParquetEvidenceRepository

def load_dataset(root,dataset_id):
    repo=ParquetEvidenceRepository(root); manifest=repo.load_manifest(dataset_id)
    if sum(a.row_count for a in manifest.artifacts)>100000:
        raise ValueError('Prototype analytics limit is 100,000 records; streaming scale-out is not implemented')
    return manifest,{kind:[model.model_validate(r) for r in pq.read_table(repo._dataset_path(dataset_id)/f'{kind}.parquet').to_pylist()] for kind,model in RECORD_MODELS.items()}
