"""Read-only runtime and artifact verification; exits nonzero on unmet assertions."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen


def hashes(path):
    return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(path.rglob("*")) if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", default="http://127.0.0.1:8000")
    parser.add_argument("--web-url")
    parser.add_argument("--dataset", type=Path, default=Path("data/sample/demo"))
    parser.add_argument("--replica", type=Path, default=Path("artifacts/replica/demo"))
    parser.add_argument("--labels", type=Path, default=Path("data/ground_truth/demo"))
    parser.add_argument("--replica-labels", type=Path, default=Path("artifacts/replica-labels/demo"))
    args = parser.parse_args()
    evidence_hashes, label_hashes = hashes(args.dataset), hashes(args.labels)
    assert evidence_hashes and evidence_hashes == hashes(args.replica), "Evidence artifacts differ"
    assert label_hashes and label_hashes == hashes(args.replica_labels), "Label artifacts differ"
    with urlopen(args.api_url + "/api/v1/health", timeout=5) as response:
        health = json.load(response)
    assert health["status"] == "ok" and health["storage_ready"] and health["registered_datasets"] == 1
    result = {"determinism": "passed", "evidence_files": len(evidence_hashes), "label_files": len(label_hashes), "backend": health}
    if args.web_url:
        with urlopen(args.web_url + "/api/status", timeout=5) as response:
            proxy = json.load(response)
        assert proxy["ok"] and proxy["health"] == health
        result["frontend_backend_connectivity"] = "passed"
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
