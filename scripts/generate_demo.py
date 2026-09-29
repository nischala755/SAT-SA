"""Generate immutable synthetic evidence; optionally register in local metadata."""
import argparse
from pathlib import Path

from sat_sa.repositories.duckdb_metadata import DuckDBMetadataRepository
from sat_sa.synthetic.generator import generate_dataset


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=20260927)
    parser.add_argument("--assessment-year", type=int, default=2025)
    parser.add_argument("--output", type=Path, default=Path("data/sample/demo"))
    parser.add_argument("--labels-output", type=Path, default=Path("data/ground_truth/demo"))
    parser.add_argument("--register", type=Path, help="Metadata DB path; stop the API before running this writer")
    args = parser.parse_args()
    manifest = generate_dataset(args.seed, args.output, args.labels_output, assessment_year=args.assessment_year)
    if args.register:
        with DuckDBMetadataRepository(args.register) as repo:
            repo.initialize()
            repo.register_dataset(manifest)
    print(manifest.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
