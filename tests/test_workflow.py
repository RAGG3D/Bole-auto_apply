from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_docs
import package_skill
import redline_scan
import token_budget
import triage
import submit
import workflow_guard as guard


def cv():
    return {"type": "cv", "name": "Example", "target_title": "Analyst",
            "profile": "Data analysis", "sections": [{"heading": "Projects", "entries": [
                {"experience_id": "p1", "role": "Team member", "org": "Local reporting tool",
                 "meta": "2024", "bullets": ["Helps analysts review local data.",
                 "Built Python scripts with local JSON storage.", "Saved two hours each week."]}]}]}


def verdict():
    return {"schema_version": 2, "company": "Example", "title": "Analyst",
            "jd_completeness": "full", "decision": "generate", "material_mode": "strict",
            "submission_policy": "authorized_only", "eligible": True, "job_open": True,
            "location_compatible": True, "domain_fit": True, "documents_complete": True,
            "employer_excluded": False, "seniority_band": "junior", "fit": 75,
            "redline_core_count": 0, "required_documents": ["cv"],
            "requirements": [{"id": "r1", "quote": "Analyse data", "source": "JD.txt",
                              "coverage": "verified", "evidence_refs": ["p1.facts[0]"]}]}


class WorkflowTests(unittest.TestCase):
    def test_redlines_match_chinese_without_spaces_but_not_english_substrings(self):
        self.assertTrue(redline_scan.term_pattern("Power BI").search("使用Power BI制作报表"))
        self.assertTrue(redline_scan.term_pattern("湿实验").search("完成湿实验流程"))
        self.assertFalse(redline_scan.term_pattern("R").search("Reporting"))

    def test_exact_upload_manifest_handles_extra_documents_and_rejects_ambiguity(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "README.md").write_text("Reviewed package")
            for name in ("Name - CV.pdf", "Old - CV.pdf", "Criteria.pdf"):
                (p / name).write_bytes(b"%PDF fixture")
            v = {"required_documents": ["cv"]}
            with self.assertRaises(submit.SubmitError):
                submit.materials(p, v)
            v.update(required_documents=["cv", "ksc"],
                     material_files={"cv": "Name - CV.pdf", "ksc": "Criteria.pdf"})
            selected = submit.materials(p, v)
            self.assertEqual(selected["cv"].name, "Name - CV.pdf")
            self.assertEqual(selected["ksc"].name, "Criteria.pdf")
            message = submit.task_message({"source": "manual"}, {}, {}, "example", {},
                                          selected["cv"], None, {"ksc": selected["ksc"]})
            self.assertIn(str(selected["ksc"]), message)
            self.assertIn("用户提供的职位链接", message)
            self.assertNotIn("如何得知职位：LinkedIn", message)
            v["material_files"]["cv"] = "../elsewhere.pdf"
            with self.assertRaises(submit.SubmitError):
                submit.materials(p, v)

    def test_ambiguous_title_is_reviewed_and_blocklist_applies_to_manual(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            candidates = [
                {"title": "Graduate Program Analyst", "company": "Example"},
                {"title": "Data Analyst", "company": "Clearance Consulting"},
                {"title": "Implementation Consultant", "company": "Example"},
                {"title": "Power BI Developer", "company": "Example"},
                {"title": "Analyst", "company": "Excluded Pty Ltd", "source": "manual"}]
            (p / "input.json").write_text(json.dumps({"candidates": candidates}))
            (p / "config.json").write_text(json.dumps({"target_titles": ["Analyst"],
                "eligibility_regex": "clearance", "redline_stack_regex": "Power BI",
                "adjacent_title_regex": "consultant", "excluded_employers": ["Excluded"]}))
            triage.bucket_candidates(p / "input.json", p / "config.json", p / "out.json")
            buckets = json.loads((p / "out.json").read_text())["buckets"]
            self.assertEqual(len(buckets["SCORE"]), 1)
            self.assertEqual(len(buckets["REVIEW"]), 3)
            self.assertEqual(len(buckets["SKIP_employer"]), 1)

    def test_complete_high_score_cannot_override_hard_gates(self):
        base = verdict()
        self.assertEqual(guard.generate_errors(base, {}), [])
        for field, value in [("jd_completeness", "stub"), ("job_open", False),
                             ("eligible", None), ("domain_fit", False),
                             ("documents_complete", False), ("seniority_band", "senior")]:
            with self.subTest(field=field):
                self.assertTrue(guard.generate_errors({**base, field: value, "fit": 99}, {}))
        self.assertTrue(guard.generate_errors(base, {"excluded_employers": ["Example Ltd"]}))

    def test_matching_tolerance_never_enables_stretch(self):
        v = verdict()
        self.assertEqual(guard.generate_errors(v, {"stretch": {"allowed": True}}), [])
        v["material_mode"] = "stretch"
        self.assertTrue(guard.generate_errors(v, {"stretch": {"allowed": True}}))

    def test_proposed_is_not_strict_verified_coverage(self):
        v = verdict()
        v["requirements"][0]["coverage"] = "proposed"
        self.assertTrue(guard.generate_errors(v, {}))
        v["requirements"][0]["coverage"] = "verified"
        v["requirements"][0]["evidence_refs"] = []
        self.assertTrue(guard.generate_errors(v, {}))

    def test_stretch_append_preserves_architecture_ownership_and_achievement(self):
        before = cv()
        after = copy.deepcopy(before)
        text = "Added a local SQL staging query before the existing Python report."
        after["sections"][0]["entries"][0]["bullets"].append(text)
        audit = {"additions": [{"experience_id": "p1", "requirement_id": "r1", "text": text,
                               "why_here": "Compatible input preparation", "basis": "Draft process",
                               "status": "proposed"}]}
        self.assertEqual(guard.stretch_errors(before, after, audit), [])
        for field, value in [("org", "Cloud platform"), ("role", "Sole founder"), ("meta", "2014")]:
            broken = copy.deepcopy(after)
            broken["sections"][0]["entries"][0][field] = value
            self.assertTrue(guard.stretch_errors(before, broken, audit))
        broken = copy.deepcopy(after)
        broken["sections"][0]["entries"][0]["bullets"][2] = "Saved 200 hours."
        self.assertTrue(guard.stretch_errors(before, broken, audit))
        broken = copy.deepcopy(after)
        broken["sections"][0]["entries"].append({"role": "Invented", "bullets": ["Untracked"]})
        self.assertTrue(guard.stretch_errors(before, broken, audit))

    def make_package(self, root):
        (root / "_content").mkdir()
        facts = root / "facts.json"
        facts.write_text(json.dumps({"red_lines": ["ForbiddenStack"], "experiences": [
            {"id": "p1", "must_include": True}]}))
        (root / "verdict.json").write_text(json.dumps(verdict()))
        (root / "_content/cv.json").write_text(json.dumps(cv()))
        (root / "tailoring.json").write_text(json.dumps({
            "identity_reviewed": True, "claims_reviewed": True,
            "coverage_reviewed": True, "layout_reviewed": True}))
        (root / "JD.txt").write_text("Analyse data")
        return facts

    def test_review_detects_title_conflict_and_missing_required_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp); facts = self.make_package(p)
            (p / "_content/cover.json").write_text(json.dumps({"target_title": "Wrong role"}))
            with self.assertRaisesRegex(guard.GuardError, "target titles"):
                guard.review(p, facts)
            (p / "_content/cover.json").unlink()
            altered = cv(); altered["sections"] = []
            (p / "_content/cv.json").write_text(json.dumps(altered))
            with self.assertRaisesRegex(guard.GuardError, "missing required experience"):
                guard.review(p, facts)

    def test_file_or_facts_change_invalidates_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp); facts = self.make_package(p)
            (p / "review.json").write_text(json.dumps(guard.review(p, facts)))
            guard.check_fresh(p, facts)
            (p / "CV.pdf").write_bytes(b"replacement")
            with self.assertRaises(guard.GuardError):
                guard.check_fresh(p, facts)
            (p / "CV.pdf").unlink()
            facts.write_text(facts.read_text() + "\n")
            with self.assertRaises(guard.GuardError):
                guard.check_fresh(p, facts)

    def test_renderer_stops_redline_before_writing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp); facts = self.make_package(p)
            data = cv(); data["profile"] = "ForbiddenStack"
            (p / "_content/cv.json").write_text(json.dumps(data))
            with self.assertRaises(build_docs.BuildError):
                build_docs.build(p / "_content/cv.json", p / "CV.pdf", 2, facts)
            self.assertFalse((p / "CV.html").exists())

    def test_pdf_overflow_fails_instead_of_unreadable_shrinking(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp); self.make_package(p)
            with mock.patch.object(build_docs, "find_browser", return_value="fake"), \
                 mock.patch.object(build_docs, "print_pdf", return_value=(True, "")), \
                 mock.patch.object(build_docs, "pdf_pages", return_value=3):
                with self.assertRaisesRegex(build_docs.BuildError, "页数仍超限"):
                    build_docs.build(p / "_content/cv.json", p / "CV.pdf", 2)

    def test_usage_keeps_cache_subset_and_separate_denominators(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "usage.jsonl"
            row = {"call_id": "1", "input_tokens": 100, "cached_input_tokens": 80, "output_tokens": 20}
            p.write_text(json.dumps(row))
            actual = token_budget.actual(p, 2, 1)
            self.assertEqual(actual["totals"]["total_tokens"], 120)
            self.assertEqual(actual["tokens_per_generated_job"], 60)
            self.assertEqual(actual["tokens_per_confirmed_submission"], 120)
            p.write_text(json.dumps(row) + "\n" + json.dumps(row))
            with self.assertRaises(ValueError):
                token_budget.actual(p, 2, 1)

    def test_stretch_estimate_never_contains_submission(self):
        result = token_budget.estimate("full", 1, stretch=True)
        self.assertNotIn("submission", [x["stage"] for x in result["per_job_stages"]])

    def test_lite_package_is_portable_without_submit_or_private_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "bole-lite"
            package_skill.package("lite", dest)
            self.assertTrue((dest / "scripts/build_docs.py").is_file())
            self.assertTrue((dest / "references/stretch.md").is_file())
            self.assertFalse((dest / "scripts/submit.py").exists())
            self.assertFalse((dest / "profile").exists())
            self.assertFalse((dest / "state").exists())
            with self.assertRaises(ValueError):
                package_skill.package("lite", dest)


if __name__ == "__main__":
    unittest.main()
