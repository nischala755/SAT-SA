import subprocess
import sys
from pathlib import Path


def test_export_is_deterministic_and_drift_fails(tmp_path):
    script = Path("scripts/export_contracts.py")
    assert script.exists(), "Contract exporter has not been implemented"
    def run(*args):
        return subprocess.run([sys.executable, str(script), "--output-root", str(tmp_path), *args], capture_output=True, text=True)
    assert run().returncode == 0
    ts = tmp_path / "packages/shared-types/src/generated.ts"
    first = ts.read_bytes()
    assert b"export type Alert" in first
    assert run().returncode == 0
    assert ts.read_bytes() == first
    assert run("--check").returncode == 0
    ts.write_text("broken contract", encoding="utf-8")
    result = run("--check")
    assert result.returncode == 1
    assert "Contract drift" in result.stdout
