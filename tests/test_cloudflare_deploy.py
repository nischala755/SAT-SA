"""Cloud demo credentials must be generated locally and never overwritten."""
import json
import os
import stat
import subprocess
import sys
from pathlib import Path


def test_cloudflare_demo_identity_is_local_and_immutable(tmp_path):
    script = Path(__file__).parents[1] / 'scripts' / 'prepare_cloudflare_demo.py'
    first = subprocess.run([sys.executable, str(script)], cwd=tmp_path, capture_output=True, text=True)
    assert first.returncode == 0
    contents = (tmp_path / '.env.cloudflare.local').read_text()
    identities = json.loads(contents.splitlines()[0].split('=', 1)[1])
    token, person = next(iter(identities.items()))
    assert len(token) >= 40
    assert person == {'actor': 'cloudflare-demo-owner', 'role': 'administrator'}
    assert token not in first.stdout
    if os.name == 'posix':
        assert stat.S_IMODE((tmp_path / '.env.cloudflare.local').stat().st_mode) == 0o600
    second = subprocess.run([sys.executable, str(script)], cwd=tmp_path, capture_output=True, text=True)
    assert second.returncode != 0
    assert (tmp_path / '.env.cloudflare.local').read_text() == contents
