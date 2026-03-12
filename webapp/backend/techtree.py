"""Dynamic tech tree builder — constructs graph from experiment descriptions."""

import re
from collections import defaultdict

# Extended keyword map for sub-node detection
CONCEPT_KEYWORDS = {
    "learning rate": "learning_rate",
    "lr": "learning_rate",
    "batch size": "batch_size",
    "warmup": "warmup",
    "warmdown": "warmdown",
    "cooldown": "warmdown",
    "depth": "depth",
    "n_embd": "embedding_dim",
    "embedding": "embedding_dim",
    "n_head": "num_heads",
    "head": "num_heads",
    "n_kv": "kv_heads",
    "head_dim": "head_dim",
    "aspect_ratio": "aspect_ratio",
    "window": "window",
    "layer": "layers",
    "weight decay": "weight_decay",
    "momentum": "momentum",
    "adam": "adam",
    "muon": "muon",
    "scheduler": "scheduler",
    "gradient": "gradient",
    "clip": "gradient",
    "activation": "activation",
    "relu": "activation",
    "gelu": "activation",
    "swiglu": "activation",
    "norm": "normalization",
    "rmsnorm": "normalization",
    "layernorm": "normalization",
    "attention": "attention",
    "residual": "residual",
    "rope": "positional",
    "rotary": "positional",
    "softcap": "softcap",
    "sequence": "sequence_len",
    "vocab": "vocab",
    "dropout": "dropout",
    "accumulation": "grad_accum",
    "precision": "precision",
}


def extract_concepts(description: str) -> list[str]:
    """Extract concept keywords from an experiment description."""
    desc_lower = description.lower()
    found = []
    for keyword, concept in CONCEPT_KEYWORDS.items():
        if keyword in desc_lower and concept not in found:
            found.append(concept)
    return found if found else ["general"]


def classify_to_tier(description: str, config: dict) -> str:
    """Classify description to tech tree tier."""
    desc_lower = description.lower()
    for tier_id, tier in config.get("tech_tree", {}).items():
        for keyword in tier.get("keywords", []):
            if keyword.lower() in desc_lower:
                return tier_id
    return "tier1_foundations"


def build_dynamic_tree(results: list[dict], config: dict) -> dict:
    """Build a dynamic tech tree graph from experiment descriptions."""
    nodes = []
    edges = []
    concept_data = defaultdict(lambda: {
        "experiments": 0, "keeps": 0, "best_bpb": None, "descriptions": []
    })
    tier_experiments = defaultdict(int)
    tier_keeps = defaultdict(int)

    for r in results:
        desc = r.get("description", "")
        tier = classify_to_tier(desc, config)
        concepts = extract_concepts(desc)
        tier_experiments[tier] += 1

        if r["status"] == "keep":
            tier_keeps[tier] += 1

        for concept in concepts:
            key = f"{tier}:{concept}"
            concept_data[key]["experiments"] += 1
            concept_data[key]["descriptions"].append(desc)
            if r["status"] == "keep":
                concept_data[key]["keeps"] += 1
                bpb = r["val_bpb"]
                if bpb > 0:
                    cur = concept_data[key]["best_bpb"]
                    if cur is None or bpb < cur:
                        concept_data[key]["best_bpb"] = bpb

    # Build tier root nodes
    tech_tree = config.get("tech_tree", {})
    total_keeps = sum(1 for r in results if r["status"] == "keep")

    for tier_id, tier_info in tech_tree.items():
        unlocked = total_keeps >= tier_info.get("unlock_requires", 0)
        status = "locked"
        if unlocked and tier_experiments[tier_id] > 0:
            status = "mastered" if tier_keeps[tier_id] > 0 else "explored"
        elif unlocked:
            status = "unlocked"

        nodes.append({
            "id": tier_id,
            "label": tier_info["name"],
            "type": "tier",
            "tier": tier_id,
            "status": status,
            "experiments": tier_experiments[tier_id],
            "keeps": tier_keeps[tier_id],
            "size": 40,
        })

    # Build concept sub-nodes
    for key, data in concept_data.items():
        tier, concept = key.split(":", 1)
        status = "explored"
        if data["keeps"] > 0:
            status = "mastered"

        node_id = f"{tier}_{concept}"
        label = concept.replace("_", " ").title()
        size = min(10 + data["experiments"] * 3, 30)

        nodes.append({
            "id": node_id,
            "label": label,
            "type": "concept",
            "tier": tier,
            "status": status,
            "experiments": data["experiments"],
            "keeps": data["keeps"],
            "best_bpb": data["best_bpb"],
            "size": size,
        })

        edges.append({
            "source": tier,
            "target": node_id,
        })

    # Add cross-tier edges for experiments touching multiple tiers
    concept_nodes = {n["id"] for n in nodes if n["type"] == "concept"}
    for r in results:
        desc = r.get("description", "")
        concepts = extract_concepts(desc)
        if len(concepts) > 1:
            tier = classify_to_tier(desc, config)
            node_ids = [f"{tier}_{c}" for c in concepts if f"{tier}_{c}" in concept_nodes]
            for i in range(len(node_ids)):
                for j in range(i + 1, len(node_ids)):
                    edge = {"source": node_ids[i], "target": node_ids[j], "type": "cross"}
                    if edge not in edges:
                        edges.append(edge)

    return {"nodes": nodes, "edges": edges}
