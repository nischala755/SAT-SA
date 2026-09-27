import importlib
import json

import pytest
from pydantic import ValidationError


def module():
    try:
        return importlib.import_module("sat_sa.config.settings")
    except ModuleNotFoundError:
        pytest.fail("Configuration loader has not been implemented")


def test_defaults_and_environment_override(tmp_path, monkeypatch):
    mod = module()
    monkeypatch.setenv("SAT_SA_STORAGE_ROOT", str(tmp_path))
    assert mod.load_settings().storage_root == tmp_path
    config = mod.load_analytics_config()
    assert config.version == "1.0.0"
    assert config.minimum_peer_entities >= 3


@pytest.mark.parametrize("data", [{"unexpected": True}, {"demo_mode": False}, {"demo_seed": -1}])
def test_bad_configuration_fails_closed(tmp_path, data):
    mod = module()
    path = tmp_path / "settings.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValidationError):
        mod.load_settings(path)


def test_malformed_configuration(tmp_path):
    mod = module()
    path = tmp_path / "broken.json"
    path.write_text("{")
    with pytest.raises(ValueError):
        mod.load_settings(path)
