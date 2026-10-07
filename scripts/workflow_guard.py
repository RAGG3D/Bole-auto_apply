#!/usr/bin/env python3
"""Deterministic routing, Stretch invariants and package freshness (not semantic truth)."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


class GuardError(ValueError):
    pass


def read(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise GuardError(f"Expected object: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate_errors(verdict: dict, config: dict) -> list[str]:
    errors = []
    def employer_key(value):
        text = re.sub(r"[^\w]+", " ", str(value or "").casefold()).strip()
        return re.sub(r"(?:\s+(?:pty|ltd|limited|inc|llc|corporation))+$", "", text).strip()
    if employer_key(verdict.get("company")) in {
        employer_key(x) for x in config.get("excluded_employers", [])
    }:
        errors.append("employer excluded by config")
    for field, expected in (("schema_version", 2), ("jd_completeness", "full"),
                            ("decision", "generate")):
        if verdict.get(field) != expected:
            errors.append(f"{field} must be {expected!r}")
    mode = verdict.get("material_mode")
    if mode not in {"strict", "stretch"}:
        errors.append("material_mode must be strict or stretch")
    if verdict.get("submission_policy") not in {"never", "manual_only", "authorized_only"}:
        errors.append("missing/invalid submission_policy")
    if mode == "stretch":
        auth = verdict.get("stretch_authorization", {})
        if not isinstance(auth, dict) or not auth.get("user_request") or not auth.get("scope"):
            errors.append("Stretch needs an explicit user request and scope")
        if verdict.get("submission_policy") != "never":
            errors.append("Stretch submission_policy must be never")
    for field in ("eligible", "job_open", "location_compatible", "domain_fit", "documents_complete"):
        if verdict.get(field) is not True:
            errors.append(f"{field} must be confirmed true")
    if verdict.get("employer_excluded") is not False:
        errors.append("employer_excluded must be confirmed false")
    if verdict.get("seniority_band", "").lower() not in {"entry", "junior", "mid", "unspec"}:
        errors.append("seniority gate")
    requirements = verdict.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        errors.append("missing JD requirement/evidence matrix")
    else:
        seen = set()
        for row in requirements:
            if not isinstance(row, dict) or not row.get("id") or row.get("id") in seen:
                errors.append("invalid/duplicate requirement id")
                continue
            seen.add(row["id"])
            if not row.get("quote") or not row.get("source"):
                errors.append(f"{row['id']}: missing JD quote/source")
            if row.get("coverage") not in {"verified", "transferable", "gap", "proposed"}:
                errors.append(f"{row['id']}: invalid coverage")
            if row.get("coverage") == "verified" and not row.get("evidence_refs"):
                errors.append(f"{row['id']}: verified needs evidence_refs")
            if mode == "strict" and row.get("coverage") == "proposed":
                errors.append(f"{row['id']}: proposed claims require Stretch")
    try:
        fit = float(verdict["fit"])
        core = int(verdict["redline_core_count"])
        threshold = float(config.get("generate_threshold", 70))
        tolerance = config.get("match_tolerance", config.get("stretch", {}))
        if tolerance.get("allowed", True) and tolerance.get("max_level") != "保守":
            floor = float(config.get("junior_generate_floor", 60))
            if tolerance.get("max_level") == "激进":
                floor = max(55, floor - 5)
            threshold = min(threshold, floor)
        if not 0 <= fit <= 100 or fit < threshold or not 0 <= core <= 1:
            errors.append("fit/core red-line gate")
    except (ValueError, TypeError, KeyError):
        errors.append("invalid fit/redline_core_count/config")
    return errors


def submission_errors(verdict: dict) -> list[str]:
    errors = []
    # Explicit markers work for older packs too; force cannot override these.
    if verdict.get("material_mode") == "stretch":
        errors.append("Stretch documents cannot be uploaded or submitted")
    if verdict.get("workflow_variant") == "lite":
        errors.append("Bole Lite requires manual submission")
    if verdict.get("submission_policy") in {"never", "manual_only"}:
        errors.append("package submission policy forbids automation")
    return errors


def entries(cv: dict) -> dict:
    result = {}
    for section in cv.get("sections", []):
        for entry in section.get("entries", []):
            key = entry.get("experience_id")
            if key:
                if key in result:
                    raise GuardError(f"Duplicate experience_id: {key}")
                result[key] = entry
    return result


def stretch_errors(baseline: dict, cv: dict, tailoring: dict) -> list[str]:
    """Stretch adds implementation bullets; it never replaces baseline identity/claims."""
    errors = []
    before, after = entries(baseline), entries(cv)
    if not before or set(before) != set(after):
        return ["Stretch must retain all baseline experience IDs"]
    if {k: v for k, v in baseline.items() if k != "sections"} != {
        k: v for k, v in cv.items() if k != "sections"
    }:
        errors.append("Stretch must preserve baseline profile, skills metadata and contact")
    changes = tailoring.get("additions", [])
    if not isinstance(changes, list):
        return ["tailoring.additions must be an array"]
    for key, original in before.items():
        current = after[key]
        for field in set(original) | set(current):
            if field != "bullets" and current.get(field) != original.get(field):
                errors.append(f"{key}: changed baseline field {field}")
        old = original.get("bullets", [])
        new = current.get("bullets", [])
        if new[:len(old)] != old:
            errors.append(f"{key}: original purpose/architecture/achievements must remain first and unchanged")
        extra = new[len(old):]
        recorded = [r.get("text") for r in changes if r.get("experience_id") == key]
        if extra != recorded:
            errors.append(f"{key}: added bullets must exactly match tailoring.additions")
    # Non-experience sections (education, skills) must not silently gain invented facts.
    baseline_other = [s for s in baseline.get("sections", [])
                      if not any(e.get("experience_id") for e in s.get("entries", []))]
    cv_other = [s for s in cv.get("sections", [])
                if not any(e.get("experience_id") for e in s.get("entries", []))]
    if baseline_other != cv_other:
        errors.append("Stretch changed baseline education/skills sections")
    # Freeze section structure and every untagged entry, including mixed sections.
    def structure(doc):
        result = []
        for section in doc.get("sections", []):
            value = {k: v for k, v in section.items() if k != "entries"}
            value["entries"] = [e.get("experience_id") or e for e in section.get("entries", [])]
            result.append(value)
        return result
    if structure(baseline) != structure(cv):
        errors.append("Stretch changed section structure or untagged entries")
    for change in changes:
        if change.get("experience_id") not in before:
            errors.append("addition targets an unknown experience")
        if not all(change.get(k) for k in ("requirement_id", "text", "why_here", "basis")):
            errors.append("addition needs requirement_id, text, why_here and basis")
        if change.get("status") not in {"verified", "proposed"}:
            errors.append("addition status must be verified or proposed")
    return errors


def package_files(job: Path) -> list[Path]:
    return sorted([job / "verdict.json", job / "tailoring.json", job / "JD.txt",
                   *job.glob("*.pdf"), *job.glob("*.html"),
                   *(job / "_content").glob("*.json"),
                   *(job / "_baseline").glob("*.json")])


def review(job: Path, facts_path: Path) -> dict:
    # Imported lazily so this module also works through importlib in tests.
    from redline_scan import scan
    verdict = read(job / "verdict.json")
    cv = read(job / "_content/cv.json")
    audit = read(job / "tailoring.json")
    facts = read(facts_path)
    errors = []
    if verdict.get("material_mode") not in {"strict", "stretch"}:
        errors.append("unknown material_mode")
    if verdict.get("material_mode") == "stretch":
        auth = verdict.get("stretch_authorization", {})
        if (verdict.get("submission_policy") != "never" or not auth.get("user_request")
                or not auth.get("scope")):
            errors.append("Stretch needs scoped authorization and submission_policy=never")
    if verdict.get("workflow_variant") == "lite" and verdict.get("submission_policy") not in {"manual_only", "never"}:
        errors.append("Lite must require manual submission")
    present = entries(cv)
    known = {e["id"]: e for e in facts.get("experiences", [])}
    if set(present) - set(known):
        errors.append("CV contains unknown experience IDs")
    for key, experience in known.items():
        if experience.get("must_include") and key not in present:
            errors.append(f"missing required experience: {key}")
    if cv.get("target_title") != verdict.get("title"):
        errors.append("CV target_title differs from advertised title")
    cover_path = job / "_content/cover.json"
    if cover_path.exists() and read(cover_path).get("target_title") != cv.get("target_title"):
        errors.append("CV/cover target titles differ")
    if not (job / "JD.txt").is_file():
        errors.append("missing complete JD snapshot")
    required = verdict.get("required_documents", ["cv"])
    if not isinstance(required, list) or "cv" not in required:
        errors.append("required_documents must contain cv")
    else:
        for kind in required:
            if not isinstance(kind, str) or not kind.isidentifier() or not (job / "_content" / f"{kind}.json").is_file():
                errors.append(f"missing required document: {kind}")
    for field in ("identity_reviewed", "claims_reviewed", "coverage_reviewed", "layout_reviewed"):
        if audit.get(field) is not True:
            errors.append(f"tailoring.{field} not reviewed")
    if verdict.get("material_mode") == "stretch":
        errors += stretch_errors(read(job / "_baseline/cv.json"), cv, audit)
        ids = {r["id"] for r in verdict.get("requirements", [])}
        if any(r.get("requirement_id") not in ids for r in audit.get("additions", [])):
            errors.append("Stretch addition references unknown JD requirement")
    if scan(facts_path, job / "_content"):
        errors.append("red-line scan failed")
    if errors:
        raise GuardError("; ".join(errors))
    return {"schema_version": 1, "facts_sha256": digest(facts_path),
            "files": {str(p.relative_to(job)): digest(p) for p in package_files(job)}}


def check_fresh(job: Path, facts_path: Path) -> None:
    manifest = read(job / "review.json")
    current = {str(p.relative_to(job)): digest(p) for p in package_files(job)}
    if manifest.get("files") != current or manifest.get("facts_sha256") != digest(facts_path):
        raise GuardError("Package/profile changed since review; rebuild and review again")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["generate", "review", "submit"])
    parser.add_argument("--verdict", type=Path)
    parser.add_argument("--job", type=Path)
    parser.add_argument("--facts", type=Path, default=Path("profile/facts.json"))
    parser.add_argument("--config", type=Path, default=Path("profile/config.json"))
    args = parser.parse_args()
    try:
        if args.phase == "review":
            if not args.job:
                raise GuardError("--job required")
            result = review(args.job, args.facts)
            (args.job / "review.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        else:
            path = args.verdict or (args.job / "verdict.json" if args.job else None)
            if path is None:
                raise GuardError("--verdict or --job required")
            verdict = read(path)
            errors = generate_errors(verdict, read(args.config))
            if args.phase == "submit":
                errors += submission_errors(verdict)
                if not args.job:
                    errors.append("--job required")
            if errors:
                raise GuardError("; ".join(errors))
            if args.phase == "submit":
                check_fresh(args.job, args.facts)
        print("PASS")
        return 0
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
