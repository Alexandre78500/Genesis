"""File watcher — polls results.tsv, state.json, run.log for changes."""

import asyncio

from .config import HISTORY_TSV, POLL_INTERVAL_S, RESULTS_TSV, RUN_LOG, STATE_JSON
from .data import (
    compute_stats,
    evaluate_achievements,
    get_tech_tree_progress,
    load_history,
    load_results,
    parse_run_log_step,
)
from .sse import SSEManager
from .techtree import build_dynamic_tree


class FileWatcher:
    def __init__(self, sse: SSEManager):
        self.sse = sse
        self._results_mtime: float = 0
        self._state_mtime: float = 0
        self._runlog_size: int = 0
        self._last_result_count: int = 0

    async def watch_loop(self):
        # Initialize counts from existing data
        try:
            results = load_results()
            self._last_result_count = len(results)
        except Exception:
            pass

        while True:
            try:
                await self._check_results()
                await self._check_runlog()
            except Exception:
                pass
            await asyncio.sleep(POLL_INTERVAL_S)

    async def _check_results(self):
        if not RESULTS_TSV.exists():
            return
        stat = RESULTS_TSV.stat()
        if stat.st_mtime <= self._results_mtime:
            return

        self._results_mtime = stat.st_mtime
        results = load_results()

        if len(results) <= self._last_result_count:
            return

        new_results = results[self._last_result_count:]
        self._last_result_count = len(results)

        # Append new results to cumulative history
        self._append_to_history(new_results)

        # Broadcast each new result
        for i, r in enumerate(new_results):
            result_with_index = {**r, "index": len(results) - len(new_results) + i}
            # Check if this is a new best
            valid_bpbs = [e["val_bpb"] for e in results[:result_with_index["index"]] if e["val_bpb"] > 0]
            if r["val_bpb"] > 0 and (not valid_bpbs or r["val_bpb"] < min(valid_bpbs)):
                result_with_index["is_new_best"] = True
            await self.sse.broadcast("new_result", result_with_index)

        # Recompute and broadcast stats
        stats = compute_stats(results)
        serializable_stats = {k: list(v) if isinstance(v, set) else v for k, v in stats.items()}
        await self.sse.broadcast("stats_update", serializable_stats)

        # Check achievements
        from .data import load_config
        newly_unlocked, _ = evaluate_achievements()
        for ach in newly_unlocked:
            await self.sse.broadcast("achievement_unlocked", ach)

        # Update tech tree
        config = load_config()
        tree = build_dynamic_tree(results, config)
        await self.sse.broadcast("techtree_update", tree)

    def _append_to_history(self, new_results: list[dict]):
        """Append new results to cumulative history.tsv (never reset by agent)."""
        try:
            needs_header = not HISTORY_TSV.exists() or HISTORY_TSV.stat().st_size == 0
            with open(HISTORY_TSV, "a") as f:
                if needs_header:
                    f.write("commit\tval_bpb\tmemory_gb\tstatus\tdescription\n")
                for r in new_results:
                    f.write(f"{r['commit']}\t{r['val_bpb']}\t{r['memory_gb']}\t{r['status']}\t{r.get('description', '')}\n")
        except Exception:
            pass

    async def _check_runlog(self):
        if not RUN_LOG.exists():
            return
        stat = RUN_LOG.stat()
        if stat.st_size == self._runlog_size:
            return

        self._runlog_size = stat.st_size
        try:
            with open(RUN_LOG, "r", errors="replace") as f:
                content = f.read()
            step_data = parse_run_log_step(content)
            if step_data:
                await self.sse.broadcast("training_progress", step_data)
        except Exception:
            pass
