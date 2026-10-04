"""Configuration loading from YAML files in configs/."""
from __future__ import annotations
import functools
from pathlib import Path
import yaml
from src.constants import CONFIGS


@functools.lru_cache(maxsize=16)
def load(name: str) -> dict:
    p = Path(CONFIGS) / f"{name}.yaml"
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def sources() -> dict: return load("sources")
def regions() -> dict: return load("regions")
def thresholds() -> dict: return load("thresholds")
def confidence() -> dict: return load("confidence")
def pipeline() -> dict: return load("pipeline")
def ui() -> dict: return load("ui")
