#!/usr/bin/env python3
"""Build a self-contained skill using a public-resource allowlist, never runtime data."""
import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def package(variant: str, out: Path) -> None:
    if out.exists():
        raise ValueError(f"Destination already exists: {out}")
    out.mkdir(parents=True)
    shutil.copy2(ROOT / ("SKILL.md" if variant == "full" else "bole-lite/SKILL.md"), out / "SKILL.md")
    if variant == "full":
        shutil.copy2(ROOT / "install.sh", out / "install.sh")
        for folder in ("references", "templates", "data", "bole-lite"):
            shutil.copytree(ROOT / folder, out / folder)
        (out / "scripts").mkdir()
        for script in (ROOT / "scripts").glob("*.py"):
            if script.name != "package_skill.py":
                shutil.copy2(script, out / "scripts" / script.name)
        # Full entrypoint mentions the independent plugin; ship only its documentation.
        dest = out / "plugins/assholassin"
        dest.mkdir(parents=True)
        shutil.copy2(ROOT / "plugins/assholassin/README.md", dest / "README.md")
    else:
        (out / "references").mkdir()
        for name in ("materials.md", "contracts.md", "stretch.md", "token-budget.md"):
            shutil.copy2(ROOT / "references" / name, out / "references" / name)
        # contracts contains an optional full setup reference, so include that small schema.
        (out / "references/workflows").mkdir()
        shutil.copy2(ROOT / "references/workflows/setup.md", out / "references/workflows/setup.md")
        shutil.copytree(ROOT / "templates", out / "templates")
        (out / "scripts").mkdir()
        for name in ("sources.py", "redline_scan.py", "build_docs.py", "workflow_guard.py", "token_budget.py"):
            shutil.copy2(ROOT / "scripts" / name, out / "scripts" / name)
    shutil.copy2(ROOT / "LICENSE", out / "LICENSE")
    (out / ".gitignore").write_text("profile/\nApplications/\nstate/\n__pycache__/\n*.pyc\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--variant", choices=["full", "lite"], required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    try:
        package(args.variant, args.out.resolve())
    except (OSError, ValueError) as exc:
        p.exit(1, f"{exc}\n")
    print(args.out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
