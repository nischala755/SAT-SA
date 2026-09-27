"""Single-writer demo initialization, executed before starting the API worker."""
from sat_sa.config.settings import Settings, load_settings
from sat_sa.repositories.duckdb_metadata import DuckDBMetadataRepository
from sat_sa.repositories.parquet_evidence import ParquetEvidenceRepository
from .generator import generate_dataset


def ensure_demo(settings: Settings):
    root = settings.storage_root
    evidence, labels = root / "evidence/demo", root / "ground_truth/demo"
    if not evidence.exists():
        manifest = generate_dataset(settings.demo_seed, evidence, labels)
    else:
        manifest = ParquetEvidenceRepository(evidence.parent).load_manifest("demo")
        if manifest.seed != settings.demo_seed:
            raise ValueError("Existing dataset seed differs from configured seed; use a new storage root")
        if not (labels / "labels.json").is_file():
            raise ValueError("Incomplete demo generation: separate ground-truth labels are missing")
    with DuckDBMetadataRepository(root / "metadata.duckdb") as repository:
        repository.initialize()
        existing = repository.get_dataset(manifest.dataset_id)
        if existing is None:
            repository.register_dataset(manifest)
        elif existing.model_dump() != manifest.model_dump():
            raise ValueError("Immutable dataset registration differs from stored evidence")
    return manifest


if __name__ == "__main__":
    print(ensure_demo(load_settings()).model_dump_json())
