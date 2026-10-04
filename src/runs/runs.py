"""Operational run history (JSONL under data/artifacts)."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

from src.constants import DATA_ARTIFACTS

RUN_FILE = DATA_ARTIFACTS / "run_history.jsonl"


def record_run(info: dict) -> None:
    DATA_ARTIFACTS.mkdir(parents=True, exist_ok=True)
    info = dict(info)
    info.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    with open(RUN_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(info, default=str) + "\n")


def list_runs(limit: int = 50) -> list[dict]:
    if not RUN_FILE.exists():
        return []
    lines = RUN_FILE.read_text(encoding="utf-8").strip().splitlines()
    runs = [json.loads(l) for l in lines if l.strip()]
    return runs[-limit:][::-1]
