# GHOST.config: Configuration management for the GHOST algorithm

import json
from typing import Any, Dict
import os

try:
    import yaml
except ImportError:
    yaml = None

def load_config(path: str) -> Dict[str, Any]:
    """
    Load configuration for the GHOST algorithm from a YAML or JSON file.
    Args:
        path: Path to config file (YAML or JSON).
    Returns:
        config: Dictionary of configuration parameters.
    Example:
        >>> config = load_config('examples/config.yaml')
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    ext = os.path.splitext(path)[1].lower()
    with open(path, 'r') as f:
        if ext in ['.yaml', '.yml']:
            if yaml is None:
                raise ImportError("PyYAML is required for YAML config files.")
            return yaml.safe_load(f)
        elif ext == '.json':
            return json.load(f)
        else:
            raise ValueError("Config file must be .yaml, .yml, or .json")

def merge_config(defaults: Dict[str, Any], file_config: Dict[str, Any], cli_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge default, file, and CLI config dictionaries for GHOST (CLI > file > defaults).
    Args:
        defaults: Default config dict.
        file_config: Config loaded from file.
        cli_args: Config from CLI arguments (parsed by typer).
    Returns:
        Merged config dict.
    Example:
        >>> config = merge_config(defaults, file_config, cli_args)
    """
    config = defaults.copy()
    config.update(file_config or {})
    config.update({k: v for k, v in cli_args.items() if v is not None})
    return config 