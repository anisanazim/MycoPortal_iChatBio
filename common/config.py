import os
from pathlib import Path
import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_YAML_PATH = PROJECT_ROOT / "env.yaml"

def get_config_value(key: str, default: str = None) -> str:
    """Get configuration value from environment or env.yaml file"""
    value = os.getenv(key)
    if value:
        return value

    try:
        with ENV_YAML_PATH.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
            return config.get(key, default)
    except FileNotFoundError:
        return default