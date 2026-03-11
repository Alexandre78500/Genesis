"""
Autoresearch Lab Dashboard — Terminal-based real-time monitoring.
Usage: uv run gamification/dashboard.py [--watch]
"""

import sys
import os
import time
import json
from pathlib import Path

# Add parent to path so we can import engine
sys.path.insert(0, str(Path(__file__).parent))
from engine import load_results, get_full_status, load_config

TIER_SYMBOLS = {"bronze": "●", "silver": "◆", "gold": "★", "platinum": "✦"}
STATUS_SYMBOLS = {"keep": "✓", "discard": "✗", "crash": "💥"}


def clear_screen():
    os.system("clear" if os.name != "nt" else "cls")


def bar(value, max_value, width=30, fill="█", empty="░"):
    if max_value == 0:
        return empty * width
    ratio = min(value / max_value, 1.0)
    filled = int(ratio * width)
    return fill * filled + empty * (width - filled)


def format_bpb(val):
    if val is None or val == 0:
        return "---"
    return f"{val:.6f}"


def render_header():
    return [
        "╔══════════════════════════════════════════════════════════════════╗",
        "║              AUTORESEARCH LAB — FACTORY DASHBOARD              ║",
        "╚══════════════════════════════════════════════════════════════════╝",
    ]


def render_stats(stats):
    lines = ["", "┌─ METRICS ─────────────────────────────────────────────────────┐"]

    best = format_bpb(stats.get("best_bpb"))
    base = format_bpb(stats.get("baseline_bpb"))

    improvement = ""
    if stats.get("best_bpb") and stats.get("baseline_bpb") and stats["baseline_bpb"] > 0:
        pct = (stats["baseline_bpb"] - stats["best_bpb"]) / stats["baseline_bpb"] * 100
        improvement = f"  ({pct:+.3f}%)"

    lines.append(f"│  Best val_bpb:  {best}{improvement}")
    lines.append(f"│  Baseline:      {base}")
    lines.append(f"│")

    total = stats["total_runs"]
    keeps = stats["total_keeps"]
    discards = stats["total_discards"]
    crashes = stats["total_crashes"]
    rate = stats["success_rate"]

    lines.append(f"│  Experiments:   {total}  [✓ {keeps}  ✗ {discards}  💥 {crashes}]")
    lines.append(f"│  Success rate:  {bar(rate, 100, 20)} {rate:.1f}%")
    lines.append(f"│  Streak:        {stats['consecutive_keeps']} (max: {stats['max_consecutive_keeps']})")
    lines.append(f"└───────────────────────────────────────────────────────────────┘")
    return lines


def render_achievements(achievements):
    lines = ["", "┌─ ACHIEVEMENTS ────────────────────────────────────────────────┐"]

    unlocked = [a for a in achievements if a["unlocked"]]
    locked = [a for a in achievements if not a["unlocked"]]

    if unlocked:
        for a in unlocked:
            sym = TIER_SYMBOLS.get(a["tier"], "●")
            lines.append(f"│  {sym} {a['icon']} {a['name']:20s}  {a['description']}")
    else:
        lines.append(f"│  (aucun achievement débloqué)")

    if locked:
        lines.append(f"│")
        lines.append(f"│  Verrouillés: {len(locked)} restants")
        for a in locked[:3]:
            lines.append(f"│    ○ {a['name']:20s}  {a['description']}")
        if len(locked) > 3:
            lines.append(f"│    ... et {len(locked) - 3} de plus")

    lines.append(f"└───────────────────────────────────────────────────────────────┘")
    return lines


def render_tech_tree(tree):
    lines = ["", "┌─ TECH TREE ───────────────────────────────────────────────────┐"]

    for tier_id, info in tree.items():
        lock = "🔓" if info["unlocked"] else "🔒"
        exp_bar = bar(info["experiments"], max(info["experiments"], 10), 10)
        lines.append(
            f"│  {lock} {info['name']:14s}  "
            f"Exp: {info['experiments']:3d}  Keeps: {info['keeps']:3d}  {exp_bar}"
        )

    lines.append(f"└───────────────────────────────────────────────────────────────┘")
    return lines


def render_recent(results, n=8):
    lines = ["", "┌─ RECENT EXPERIMENTS ──────────────────────────────────────────┐"]

    if not results:
        lines.append("│  (aucun experiment)")
    else:
        for r in results[-n:]:
            sym = STATUS_SYMBOLS.get(r["status"], "?")
            bpb = format_bpb(r["val_bpb"])
            desc = r.get("description", "")[:40]
            lines.append(f"│  {sym} {bpb}  {r['commit'][:7]:7s}  {desc}")

    lines.append(f"└───────────────────────────────────────────────────────────────┘")
    return lines


def render_bpb_sparkline(results):
    """Mini ASCII graph of val_bpb over time."""
    lines = ["", "┌─ PROGRESSION ─────────────────────────────────────────────────┐"]

    valid = [r["val_bpb"] for r in results if r["val_bpb"] > 0]
    if len(valid) < 2:
        lines.append("│  (pas assez de données pour le graphe)")
        lines.append(f"└───────────────────────────────────────────────────────────────┘")
        return lines

    min_v, max_v = min(valid), max(valid)
    span = max_v - min_v if max_v > min_v else 0.001
    height = 6
    width = min(len(valid), 60)

    # Resample if too many points
    if len(valid) > width:
        step = len(valid) / width
        sampled = [valid[int(i * step)] for i in range(width)]
    else:
        sampled = valid

    # Build grid
    grid = [[" "] * len(sampled) for _ in range(height)]
    for col, v in enumerate(sampled):
        row = int((1 - (v - min_v) / span) * (height - 1))
        row = max(0, min(height - 1, row))
        grid[row][col] = "█"

    for i, row in enumerate(grid):
        if i == 0:
            label = f"{max_v:.4f}"
        elif i == height - 1:
            label = f"{min_v:.4f}"
        else:
            label = "       "
        lines.append(f"│  {label} │{''.join(row)}│")

    lines.append(f"└───────────────────────────────────────────────────────────────┘")
    return lines


def render_dashboard():
    """Render the full dashboard and return as string."""
    status = get_full_status()
    results = load_results()

    output = []
    output.extend(render_header())
    output.extend(render_stats(status["stats"]))
    output.extend(render_bpb_sparkline(results))
    output.extend(render_recent(results))
    output.extend(render_achievements(status["achievements"]))
    output.extend(render_tech_tree(status["tech_tree"]))

    # Newly unlocked notifications
    if status["newly_unlocked"]:
        output.append("")
        output.append("🎉 ACHIEVEMENT UNLOCKED!")
        for a in status["newly_unlocked"]:
            output.append(f"   {a['icon']} {a['name']} — {a['description']}")

    output.append("")
    output.append(f"  Last update: {time.strftime('%H:%M:%S')}")
    return "\n".join(output)


def main():
    watch = "--watch" in sys.argv

    if watch:
        try:
            while True:
                clear_screen()
                print(render_dashboard())
                time.sleep(10)
        except KeyboardInterrupt:
            print("\nDashboard stopped.")
    else:
        print(render_dashboard())


if __name__ == "__main__":
    main()
