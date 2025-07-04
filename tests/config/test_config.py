import os
import tempfile
import json
import pytest
from homegrid.config import load_config, merge_config

try:
    import yaml
except ImportError:
    yaml = None

def test_load_config_json(tmp_path):
    config_data = {"a": 1, "b": 2}
    config_path = tmp_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(config_data, f)
    config = load_config(str(config_path))
    assert config == config_data

def test_load_config_yaml(tmp_path):
    if yaml is None:
        pytest.skip("PyYAML not installed")
    config_data = {"a": 1, "b": 2}
    config_path = tmp_path / "config.yaml"
    with open(config_path, "w") as f:
        yaml.safe_dump(config_data, f)
    config = load_config(str(config_path))
    assert config == config_data

def test_merge_config():
    defaults = {"a": 1, "b": 2, "c": 3}
    file_config = {"b": 20}
    cli_args = {"c": 30, "d": None}
    merged = merge_config(defaults, file_config, cli_args)
    assert merged["a"] == 1
    assert merged["b"] == 20
    assert merged["c"] == 30
    assert "d" not in merged or merged["d"] is None 