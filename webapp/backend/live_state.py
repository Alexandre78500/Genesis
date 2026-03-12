"""Persistent live training state for the dashboard."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone

from .config import LIVE_STATE_JSON

MAX_RECENT_STEPS = 100
INTERNAL_KEYS = {"result_count_at_start", "terminal_at"}


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_live_state() -> dict:
    return {
        "status": "idle",
        "run_id": None,
        "started_at": None,
        "last_seen_at": None,
        "last_log_mtime": None,
        "last_step_at": None,
        "current_step": None,
        "recent_steps": [],
        "last_result": None,
        "status_message": "awaiting next experiment",
        "result_count_at_start": None,
        "terminal_at": None,
    }


def load_live_state() -> dict:
    if not LIVE_STATE_JSON.exists():
        return default_live_state()
    try:
        with open(LIVE_STATE_JSON) as f:
            raw = json.load(f)
    except Exception:
        return default_live_state()

    state = default_live_state()
    state.update(raw if isinstance(raw, dict) else {})
    if not isinstance(state.get("recent_steps"), list):
        state["recent_steps"] = []
    state["recent_steps"] = state["recent_steps"][-MAX_RECENT_STEPS:]
    return state


def save_live_state(state: dict):
    LIVE_STATE_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(LIVE_STATE_JSON, "w") as f:
        json.dump(state, f, indent=2)


def append_recent_step(state: dict, sample: dict):
    samples = list(state.get("recent_steps") or [])
    samples.append(sample)
    state["recent_steps"] = samples[-MAX_RECENT_STEPS:]
    state["current_step"] = {k: v for k, v in sample.items() if k != "observed_at"}
    state["last_step_at"] = sample.get("observed_at")


def export_live_state(state: dict) -> dict:
    payload = deepcopy(state)
    for key in INTERNAL_KEYS:
        payload.pop(key, None)
    payload["recent_steps"] = list(payload.get("recent_steps") or [])
    return payload


def parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None
