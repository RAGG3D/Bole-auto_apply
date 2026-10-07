#!/usr/bin/env python3
"""Scenario estimates or sums of per-call usage. Tokens, not currency or measured promises."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

# (calls per generated job, mean input/call, mean output/call).
# Includes the instructions, rolling context and tool returns in each call's input.
STAGES = {
    "full": {
        "discovery_amortized": (1, 6000, 500),
        "matching": (2, 5000, 700),
        "documents": (2, 9000, 1600),
        "review_render": (2, 10000, 800),
        "submission": (5, 12000, 350),
        "verification": (1, 8000, 250),
    },
    "lite": {
        "jd_evidence": (1, 5000, 600),
        "cv": (1, 7000, 1700),
        "review": (1, 9000, 800),
        "render_check": (1, 4000, 200),
    },
}


def estimate(variant: str, jobs: int, stretch: bool = False) -> dict:
    if jobs <= 0:
        raise ValueError("jobs must be positive")
    stages = dict(STAGES[variant])
    if stretch:
        # File-only run has no submission or verification calls.
        stages.pop("submission", None)
        stages.pop("verification", None)
        stages["stretch_mapping_review"] = (2, 9000, 900)
    rows = [{"stage": name, "calls": n, "input_tokens": n * i, "output_tokens": n * o}
            for name, (n, i, o) in stages.items()]
    inp = sum(r["input_tokens"] for r in rows)
    out = sum(r["output_tokens"] for r in rows)
    total = inp + out
    return {"basis": "planning scenario, not a measured average", "variant": variant,
            "stretch": stretch, "generated_jobs": jobs, "per_job_stages": rows,
            "per_job": {"input_tokens": inp, "output_tokens": out, "total_tokens": total,
                        "planning_low": round(total * 0.5), "planning_high": total * 3},
            "batch_total_tokens": total * jobs,
            "assumptions": "Full: 3 candidates per generated pack, compact context, 5 ATS calls, 1 verify. Lite: CV only. Cached input is included in input; hidden reasoning is included only if provider output reports it."}


def actual(path: Path, generated_jobs: int, submitted_jobs: int) -> dict:
    if generated_jobs <= 0 or not 0 <= submitted_jobs <= generated_jobs:
        raise ValueError("require generated_jobs > 0 and 0 <= submitted_jobs <= generated_jobs")
    totals = {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0}
    seen = set()
    stages = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if not row.get("call_id") or row["call_id"] in seen:
            raise ValueError("missing/duplicate call_id; use per-call usage, not cumulative counters")
        seen.add(row["call_id"])
        numbers = {k: row.get(k, 0) for k in totals}
        if any(type(v) is not int or v < 0 for v in numbers.values()):
            raise ValueError("usage fields must be nonnegative integers")
        if numbers["cached_input_tokens"] > numbers["input_tokens"]:
            raise ValueError("cached_input_tokens must be a subset of input_tokens")
        for k, v in numbers.items():
            totals[k] += v
        stage = row.get("stage", "unclassified")
        stages[stage] = stages.get(stage, 0) + numbers["input_tokens"] + numbers["output_tokens"]
    if not seen:
        raise ValueError("empty usage file")
    totals["total_tokens"] = totals["input_tokens"] + totals["output_tokens"]
    totals["uncached_input_tokens"] = totals["input_tokens"] - totals["cached_input_tokens"]
    return {"basis": "observed per-call usage supplied by operator", "calls": len(seen),
            "totals": totals, "stage_total_tokens": stages,
            "generated_jobs": generated_jobs, "confirmed_submitted_jobs": submitted_jobs,
            "tokens_per_generated_job": totals["total_tokens"] / generated_jobs,
            "tokens_per_confirmed_submission": totals["total_tokens"] / submitted_jobs if submitted_jobs else None}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--variant", choices=["full", "lite"], default="full")
    p.add_argument("--jobs", type=int, default=1)
    p.add_argument("--stretch", action="store_true")
    p.add_argument("--usage", type=Path, help="JSONL per-call usage including all agents/tools")
    p.add_argument("--submitted", type=int, default=0)
    a = p.parse_args()
    try:
        result = actual(a.usage, a.jobs, a.submitted) if a.usage else estimate(a.variant, a.jobs, a.stretch)
    except (OSError, ValueError, TypeError) as exc:
        p.exit(1, f"{exc}\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
