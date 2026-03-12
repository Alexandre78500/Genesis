"""Data layer — wraps gamification/engine.py and adds git/run.log access."""

from __future__ import annotations

import csv
import re
import subprocess
import sys

from .config import HISTORY_TSV, PROJECT_ROOT, RUN_LOG
from .live_state import export_live_state, load_live_state
from .techtree import build_dynamic_tree

# Allow importing from gamification/
sys.path.insert(0, str(PROJECT_ROOT))
from gamification.engine import (
    compute_stats,
    evaluate_achievements,
    load_config,
    load_results,
    load_state,
)

STEP_RE = re.compile(
    r"step (\d+) \(([0-9.]+)%\) \| loss: ([0-9.]+) \| "
    r"lrm: ([0-9.]+) \| dt: (\d+)ms \| tok/sec: ([0-9,]+) \| "
    r"mfu: ([0-9.]+)% \| epoch: (\d+) \| remaining: (\d+)s"
)


def load_history() -> list[dict]:
    """Load cumulative history.tsv (survives agent branch resets)."""
    if not HISTORY_TSV.exists():
        return []

    rows = []
    with open(HISTORY_TSV) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            try:
                row["val_bpb"] = float(row["val_bpb"])
                row["memory_gb"] = float(row["memory_gb"])
            except (ValueError, KeyError):
                continue
            rows.append(row)
    return rows


def get_dashboard_results() -> list[dict]:
    history = load_history()
    return history if history else load_results()


def build_achievements_payload() -> list[dict]:
    config = load_config()
    state = load_state()
    unlocked_ids = set(state.get("unlocked", []))
    unlocked_at = state.get("unlocked_at", {})

    return [
        {
            **achievement,
            "unlocked": achievement["id"] in unlocked_ids,
            "unlocked_at": unlocked_at.get(achievement["id"]),
        }
        for achievement in config["achievements"]
    ]


def get_snapshot() -> dict:
    results = get_dashboard_results()
    stats = compute_stats(results)
    config = load_config()
    live_state = export_live_state(load_live_state())

    return {
        "results": results,
        "stats": {k: list(v) if isinstance(v, set) else v for k, v in stats.items()},
        "achievements": build_achievements_payload(),
        "tech_tree": build_dynamic_tree(results, config),
        "newly_unlocked": [],
        "live_run": live_state,
        "recent_steps": live_state.get("recent_steps", []),
    }


def get_results() -> list[dict]:
    return get_dashboard_results()


def get_stats() -> dict:
    results = get_dashboard_results()
    stats = compute_stats(results)
    return {k: list(v) if isinstance(v, set) else v for k, v in stats.items()}


def get_achievements() -> list[dict]:
    return build_achievements_payload()


def get_git_log(limit: int = 200) -> list[dict]:
    try:
        result = subprocess.run(
            ["git", "log", f"-{limit}", "--format=%H\t%h\t%s\t%ai"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        commits = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("\t", 3)
            if len(parts) == 4:
                commits.append({
                    "hash": parts[0],
                    "short_hash": parts[1],
                    "message": parts[2],
                    "date": parts[3],
                })
        return commits
    except Exception:
        return []


def get_git_diff(commit_hash: str) -> dict:
    try:
        stat = subprocess.run(
            ["git", "show", "--stat", "--format=", commit_hash],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        diff = subprocess.run(
            ["git", "diff", f"{commit_hash}~1..{commit_hash}", "--", "train.py"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        return {
            "hash": commit_hash,
            "stat": stat.stdout.strip(),
            "diff_text": diff.stdout[:5000],
        }
    except Exception:
        return {"hash": commit_hash, "stat": "", "diff_text": ""}


def get_run_log_tail(lines: int = 50) -> str:
    if not RUN_LOG.exists():
        return ""
    try:
        content = RUN_LOG.read_text(errors="replace")
        all_lines = content.split("\n")
        return "\n".join(all_lines[-lines:])
    except Exception:
        return ""


def parse_run_log_step(text: str) -> dict | None:
    # run.log uses \r for progress lines, find the last step line
    parts = text.replace("\r", "\n").split("\n")
    for line in reversed(parts):
        match = STEP_RE.search(line)
        if match:
            return {
                "step": int(match.group(1)),
                "progress_pct": float(match.group(2)),
                "loss": float(match.group(3)),
                "lr_mult": float(match.group(4)),
                "dt_ms": int(match.group(5)),
                "tok_per_sec": match.group(6),
                "mfu": float(match.group(7)),
                "epoch": int(match.group(8)),
                "remaining_s": int(match.group(9)),
            }
    return None
