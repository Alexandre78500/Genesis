"""File watcher — polls results.tsv and run.log for dashboard updates."""

from __future__ import annotations

import asyncio
import json
import subprocess
import time
from datetime import datetime, timezone

from .config import HISTORY_TSV, POLL_INTERVAL_S, PROJECT_ROOT, RESULTS_TSV, RUN_LOG
from .data import (
    compute_stats,
    evaluate_achievements,
    get_dashboard_results,
    get_run_log_tail,
    load_config,
    load_results,
    parse_run_log_step,
)
from .live_state import (
    append_recent_step,
    default_live_state,
    export_live_state,
    load_live_state,
    parse_iso_datetime,
    save_live_state,
    utcnow_iso,
)
from .sse import SSEManager
from .techtree import build_dynamic_tree

ACTIVE_STATUSES = {"starting", "running", "stalled", "finishing"}
TERMINAL_STATUSES = {"completed", "crashed"}
CRASH_GRACE_S = 30
TERMINAL_SUMMARY_S = 45


class FileWatcher:
    def __init__(self, sse: SSEManager):
        self.sse = sse
        self._results_mtime: float = 0
        self._last_result_count: int = 0
        self._live_state: dict = load_live_state()
        self._last_live_payload = json.dumps(export_live_state(self._live_state), sort_keys=True)
        self._last_step_signature = self._step_signature(self._live_state.get("current_step"))

    async def prime(self):
        results = load_results()
        self._last_result_count = len(results)
        self._seed_history(results)
        await self._sync_live_state(results, force=True)

    async def watch_loop(self):
        try:
            await self.prime()
        except Exception:
            pass

        while True:
            try:
                results = load_results()
                await self._check_results(results)
                await self._sync_live_state(results)
            except Exception:
                pass
            await asyncio.sleep(POLL_INTERVAL_S)

    async def _check_results(self, results: list[dict]):
        if not RESULTS_TSV.exists():
            self._last_result_count = 0
            return

        stat = RESULTS_TSV.stat()
        if len(results) < self._last_result_count:
            self._results_mtime = stat.st_mtime
            self._last_result_count = len(results)
            return

        if stat.st_mtime <= self._results_mtime and len(results) == self._last_result_count:
            return

        self._results_mtime = stat.st_mtime
        if len(results) <= self._last_result_count:
            return

        new_results = results[self._last_result_count:]
        self._last_result_count = len(results)

        self._append_to_history(new_results)
        dashboard_results = get_dashboard_results()

        for i, result in enumerate(new_results):
            result_with_index = {
                **result,
                "index": len(dashboard_results) - len(new_results) + i,
            }
            prior = [
                entry["val_bpb"]
                for entry in dashboard_results[: result_with_index["index"]]
                if entry["val_bpb"] > 0
            ]
            if result["val_bpb"] > 0 and (not prior or result["val_bpb"] < min(prior)):
                result_with_index["is_new_best"] = True
            await self.sse.broadcast("new_result", result_with_index)

        stats = compute_stats(dashboard_results)
        serializable_stats = {k: list(v) if isinstance(v, set) else v for k, v in stats.items()}
        await self.sse.broadcast("stats_update", serializable_stats)

        newly_unlocked, _ = evaluate_achievements()
        for achievement in newly_unlocked:
            await self.sse.broadcast("achievement_unlocked", achievement)

        config = load_config()
        tree = build_dynamic_tree(dashboard_results, config)
        await self.sse.broadcast("techtree_update", tree)

    def _seed_history(self, results: list[dict]):
        if not results:
            return
        if HISTORY_TSV.exists() and HISTORY_TSV.stat().st_size > 0:
            return
        self._write_history_rows(results, mode="w")

    def _append_to_history(self, new_results: list[dict]):
        if not new_results:
            return
        if not HISTORY_TSV.exists() or HISTORY_TSV.stat().st_size == 0:
            self._seed_history(load_results()[:-len(new_results)] if len(new_results) < len(load_results()) else [])
        self._write_history_rows(new_results, mode="a")

    def _write_history_rows(self, rows: list[dict], mode: str):
        HISTORY_TSV.parent.mkdir(parents=True, exist_ok=True)
        needs_header = mode == "w" or not HISTORY_TSV.exists() or HISTORY_TSV.stat().st_size == 0
        with open(HISTORY_TSV, mode) as f:
            if needs_header:
                f.write("commit\tval_bpb\tmemory_gb\tstatus\tdescription\n")
            for row in rows:
                f.write(
                    f"{row['commit']}\t{row['val_bpb']}\t{row['memory_gb']}\t"
                    f"{row['status']}\t{row.get('description', '')}\n"
                )

    async def _sync_live_state(self, results: list[dict], force: bool = False):
        before = json.dumps(self._live_state, sort_keys=True)
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()

        process = self._find_training_process()
        runlog_stat = RUN_LOG.stat() if RUN_LOG.exists() else None
        runlog_mtime = runlog_stat.st_mtime if runlog_stat else None
        step = parse_run_log_step(get_run_log_tail(200)) if runlog_stat else None

        if process:
            if self._live_state.get("status") in TERMINAL_STATUSES | {"idle"} or not self._live_state.get("run_id"):
                self._start_new_run(len(results), runlog_mtime, now_iso, results[-1] if results else None)
            self._live_state["last_seen_at"] = now_iso
            self._live_state["last_log_mtime"] = runlog_mtime
            self._live_state["terminal_at"] = None

            if step:
                signature = self._step_signature(step)
                if signature != self._last_step_signature:
                    sample = {**step, "observed_at": now_iso}
                    append_recent_step(self._live_state, sample)
                    self._last_step_signature = signature
                    await self.sse.broadcast("training_step", sample)
                elif not self._live_state.get("current_step"):
                    self._live_state["current_step"] = step

                stale_after = max((step["dt_ms"] / 1000) * 2, 120)
                if runlog_mtime is not None and time.time() - runlog_mtime > stale_after:
                    self._live_state["status"] = "stalled"
                    self._live_state["status_message"] = "waiting for next step"
                else:
                    self._live_state["status"] = "running"
                    self._live_state["status_message"] = "training metrics streaming"
            else:
                self._live_state["status"] = "starting"
                self._live_state["status_message"] = "booting / compiling"
        else:
            self._reconcile_inactive_run(results, now, now_iso)

        after = json.dumps(self._live_state, sort_keys=True)
        if force or after != before:
            save_live_state(self._live_state)
            await self._broadcast_live_state(force=force)

    def _reconcile_inactive_run(self, results: list[dict], now: datetime, now_iso: str):
        status = self._live_state.get("status")
        run_id = self._live_state.get("run_id")
        if not run_id:
            self._reset_to_idle()
            return

        result_count_at_start = self._live_state.get("result_count_at_start")
        new_result_written = (
            isinstance(result_count_at_start, int) and len(results) > result_count_at_start
        )

        if new_result_written:
            self._live_state["status"] = "completed"
            self._live_state["status_message"] = "result recorded"
            self._live_state["last_result"] = results[-1]
            self._live_state["terminal_at"] = self._live_state.get("terminal_at") or now_iso
            return

        if status in {"starting", "running", "stalled"}:
            self._live_state["status"] = "finishing"
            self._live_state["status_message"] = "evaluating / writing results"
            status = "finishing"

        if status == "finishing":
            last_seen = parse_iso_datetime(self._live_state.get("last_seen_at"))
            if last_seen and (now - last_seen).total_seconds() > CRASH_GRACE_S:
                self._live_state["status"] = "crashed"
                self._live_state["status_message"] = "process exited without result"
                self._live_state["terminal_at"] = self._live_state.get("terminal_at") or now_iso
            return

        if status in TERMINAL_STATUSES:
            terminal_at = parse_iso_datetime(self._live_state.get("terminal_at"))
            if terminal_at and (now - terminal_at).total_seconds() > TERMINAL_SUMMARY_S:
                self._reset_to_idle()
            return

        self._reset_to_idle()

    def _start_new_run(
        self,
        result_count_at_start: int,
        runlog_mtime: float | None,
        now_iso: str,
        last_result: dict | None,
    ):
        self._live_state = default_live_state()
        self._live_state.update({
            "status": "starting",
            "run_id": f"run-{now_iso}",
            "started_at": now_iso,
            "last_seen_at": now_iso,
            "last_log_mtime": runlog_mtime,
            "last_result": last_result,
            "status_message": "booting / compiling",
            "result_count_at_start": result_count_at_start,
        })
        self._last_step_signature = None

    def _reset_to_idle(self):
        last_result = self._live_state.get("last_result")
        self._live_state = default_live_state()
        self._live_state["last_result"] = last_result
        self._last_step_signature = None

    async def _broadcast_live_state(self, force: bool = False):
        payload = export_live_state(self._live_state)
        encoded = json.dumps(payload, sort_keys=True)
        if force or encoded != self._last_live_payload:
            self._last_live_payload = encoded
            await self.sse.broadcast("live_state", payload)

    def _find_training_process(self) -> dict | None:
        try:
            result = subprocess.run(
                ["ps", "-axo", "pid=,etime=,command="],
                capture_output=True,
                text=True,
                timeout=5,
            )
        except Exception:
            return None

        candidates = []
        for raw_line in result.stdout.splitlines():
            line = raw_line.strip()
            if not line or "train.py" not in line:
                continue
            parts = line.split(None, 2)
            if len(parts) < 3:
                continue
            try:
                pid = int(parts[0])
                etimes = self._parse_elapsed(parts[1])
            except ValueError:
                continue
            command = parts[2]
            if "rg " in command or "watcher.py" in command:
                continue

            score = 0
            if "python" in command:
                score += 3
            if str(PROJECT_ROOT) in command:
                score += 2
            if "uv run train.py" in command:
                score += 1
            candidates.append((score, -etimes, {"pid": pid, "etimes": etimes, "command": command}))

        if not candidates:
            return None

        candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return candidates[0][2]

    @staticmethod
    def _parse_elapsed(value: str) -> int:
        if "-" in value:
            days_part, time_part = value.split("-", 1)
            days = int(days_part)
        else:
            days = 0
            time_part = value

        chunks = [int(chunk) for chunk in time_part.split(":")]
        if len(chunks) == 2:
            hours = 0
            minutes, seconds = chunks
        elif len(chunks) == 3:
            hours, minutes, seconds = chunks
        else:
            raise ValueError("Unsupported etime format")

        return days * 86400 + hours * 3600 + minutes * 60 + seconds

    @staticmethod
    def _step_signature(step: dict | None) -> tuple | None:
        if not step:
            return None
        return (
            step.get("step"),
            step.get("progress_pct"),
            step.get("loss"),
            step.get("lr_mult"),
            step.get("dt_ms"),
            step.get("tok_per_sec"),
            step.get("mfu"),
            step.get("epoch"),
            step.get("remaining_s"),
        )
