"""
Gamification engine for autoresearch lab.
Reads results.tsv, evaluates achievements, tracks tech tree progression.
"""

import json
import csv
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
GAMIFICATION_DIR = Path(__file__).parent
CONFIG_PATH = GAMIFICATION_DIR / "config.json"
STATE_PATH = GAMIFICATION_DIR / "state.json"
RESULTS_PATH = ROOT / "results.tsv"


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def load_state():
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"unlocked": [], "unlocked_at": {}, "sessions": []}


def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def load_results():
    """Parse results.tsv into list of dicts."""
    if not RESULTS_PATH.exists():
        return []
    rows = []
    with open(RESULTS_PATH) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            try:
                row["val_bpb"] = float(row["val_bpb"])
                row["memory_gb"] = float(row["memory_gb"])
            except (ValueError, KeyError):
                continue
            rows.append(row)
    return rows


def classify_experiment(description):
    """Classify an experiment description into a tech tree category."""
    config = load_config()
    desc_lower = description.lower()
    for tier_id, tier in config["tech_tree"].items():
        for keyword in tier["keywords"]:
            if keyword.lower() in desc_lower:
                return tier_id
    return "tier1_foundations"  # default


def compute_stats(results):
    """Compute all stats needed for achievement evaluation."""
    if not results:
        return {
            "total_runs": 0, "total_keeps": 0, "total_discards": 0,
            "total_crashes": 0, "best_bpb": None, "baseline_bpb": None,
            "baseline_memory": None, "best_bpb_memory": None,
            "consecutive_keeps": 0, "max_consecutive_keeps": 0,
            "single_improvements": [], "micro_improvements": 0,
            "categories_tried": set(), "category_keeps": set(),
            "success_rate": 0.0, "improvements": [],
        }

    total_runs = len(results)
    keeps = [r for r in results if r["status"] == "keep"]
    discards = [r for r in results if r["status"] == "discard"]
    crashes = [r for r in results if r["status"] == "crash"]

    # Baseline is first result
    baseline_bpb = results[0]["val_bpb"] if results[0]["val_bpb"] > 0 else None
    baseline_memory = results[0]["memory_gb"]

    # Best bpb (lowest non-zero)
    valid_bpbs = [r["val_bpb"] for r in results if r["val_bpb"] > 0]
    best_bpb = min(valid_bpbs) if valid_bpbs else None
    best_bpb_row = min((r for r in results if r["val_bpb"] > 0), key=lambda r: r["val_bpb"], default=None)
    best_bpb_memory = best_bpb_row["memory_gb"] if best_bpb_row else None

    # Consecutive keeps (current streak)
    consecutive = 0
    for r in reversed(results):
        if r["status"] == "keep":
            consecutive += 1
        else:
            break

    # Max consecutive keeps
    max_consec = 0
    current = 0
    for r in results:
        if r["status"] == "keep":
            current += 1
            max_consec = max(max_consec, current)
        else:
            current = 0

    # Single improvements (pct change from previous keep)
    improvements = []
    prev_bpb = baseline_bpb
    micro_count = 0
    for r in results[1:]:
        if r["status"] == "keep" and r["val_bpb"] > 0 and prev_bpb and prev_bpb > 0:
            pct = (prev_bpb - r["val_bpb"]) / prev_bpb * 100
            improvements.append(pct)
            if 0 < pct < 0.1:
                micro_count += 1
            prev_bpb = r["val_bpb"]

    # Categories
    categories = set()
    category_keeps = set()
    for r in results:
        cat = classify_experiment(r.get("description", ""))
        categories.add(cat)
        if r["status"] == "keep":
            category_keeps.add(cat)

    return {
        "total_runs": total_runs,
        "total_keeps": len(keeps),
        "total_discards": len(discards),
        "total_crashes": len(crashes),
        "best_bpb": best_bpb,
        "baseline_bpb": baseline_bpb,
        "baseline_memory": baseline_memory,
        "best_bpb_memory": best_bpb_memory,
        "consecutive_keeps": consecutive,
        "max_consecutive_keeps": max_consec,
        "single_improvements": improvements,
        "micro_improvements": micro_count,
        "categories_tried": categories,
        "category_keeps": category_keeps,
        "success_rate": len(keeps) / total_runs * 100 if total_runs > 0 else 0,
        "improvements": improvements,
    }


def check_achievement(achievement, stats):
    """Check if an achievement condition is met."""
    cond = achievement["condition"]
    t = cond["type"]

    if t == "total_runs":
        return stats["total_runs"] >= cond["value"]
    elif t == "total_keeps":
        return stats["total_keeps"] >= cond["value"]
    elif t == "single_improvement_pct":
        return any(imp >= cond["value"] for imp in stats["single_improvements"])
    elif t == "consecutive_keeps":
        return stats["max_consecutive_keeps"] >= cond["value"]
    elif t == "categories_tried":
        return len(stats["categories_tried"]) >= cond["value"]
    elif t == "best_bpb_below":
        return stats["best_bpb"] is not None and stats["best_bpb"] < cond["value"]
    elif t == "micro_improvements":
        return stats["micro_improvements"] >= cond["value"]
    elif t == "category_keep":
        return cond["category"] in [c.replace("tier2_", "").replace("tier3_", "").replace("tier4_", "")
                                     for c in stats["category_keeps"]]
    elif t == "better_score_less_memory":
        if stats["best_bpb"] is None or stats["baseline_bpb"] is None:
            return False
        return (stats["best_bpb"] < stats["baseline_bpb"] and
                stats["best_bpb_memory"] is not None and
                stats["baseline_memory"] is not None and
                stats["best_bpb_memory"] < stats["baseline_memory"])
    return False


def evaluate_achievements():
    """Evaluate all achievements and return newly unlocked ones."""
    config = load_config()
    state = load_state()
    results = load_results()
    stats = compute_stats(results)

    newly_unlocked = []
    for ach in config["achievements"]:
        if ach["id"] in state["unlocked"]:
            continue
        if check_achievement(ach, stats):
            state["unlocked"].append(ach["id"])
            state["unlocked_at"][ach["id"]] = datetime.now().isoformat()
            newly_unlocked.append(ach)

    save_state(state)
    return newly_unlocked, stats


def get_tech_tree_progress():
    """Get current progress through the tech tree."""
    config = load_config()
    results = load_results()
    stats = compute_stats(results)

    tree_progress = {}
    for tier_id, tier in config["tech_tree"].items():
        experiments_in_tier = sum(
            1 for r in results if classify_experiment(r.get("description", "")) == tier_id
        )
        keeps_in_tier = sum(
            1 for r in results
            if classify_experiment(r.get("description", "")) == tier_id and r["status"] == "keep"
        )
        unlocked = stats["total_keeps"] >= tier["unlock_requires"]
        tree_progress[tier_id] = {
            "name": tier["name"],
            "unlocked": unlocked,
            "experiments": experiments_in_tier,
            "keeps": keeps_in_tier,
            "unlock_requires": tier["unlock_requires"],
        }
    return tree_progress


def get_full_status():
    """Get complete gamification status for the dashboard."""
    newly_unlocked, stats = evaluate_achievements()
    config = load_config()
    state = load_state()
    tree = get_tech_tree_progress()

    all_achievements = []
    for ach in config["achievements"]:
        all_achievements.append({
            **ach,
            "unlocked": ach["id"] in state["unlocked"],
            "unlocked_at": state["unlocked_at"].get(ach["id"]),
        })

    return {
        "stats": {k: v if not isinstance(v, set) else list(v) for k, v in stats.items()},
        "achievements": all_achievements,
        "newly_unlocked": newly_unlocked,
        "tech_tree": tree,
    }


if __name__ == "__main__":
    status = get_full_status()
    print(json.dumps(status, indent=2, default=str))
