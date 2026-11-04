"""Bounded phase5 functional runner; all generated outputs stay in phase5.

Historical assertions and golden fixtures are never rewritten. Two historical
catalog identity/shape checks are classified explicitly, not hidden as passes.
"""
from pathlib import Path
import datetime as dt
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ENGINE = Path(r"C:\Project\rea-tools\godot-4.5.1\Godot_v4.5.1-stable_win64_console.exe")
OUT = ROOT / "evidence/phase5/verification" / ("functional-" + dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
BASE = [str(ENGINE), "--headless", "--path", str(ROOT), "--script"]
OLD = ["test_sim", "independent_review", "test_catalog", "phase1_independent", "phase2_independent", "phase5_regression_phase2_scene_independent", "phase3_independent", "phase5_regression_phase3_scene_independent", "phase4_math", "phase4_combat", "phase4_catalog", "phase4_scene", "phase4_legacy"]
NEW = ["phase5_equipment", "phase5_sim_storage", "phase5_skill_catalog", "phase5_scene"]
EXPECTED_HISTORY = {
    "phase3_independent": ["golden fixture uses the current unchanged catalog"],
    "phase4_catalog": ["three skill and ten stat definitions"],
}
PREFIXES = {"test_sim": "BASELINE_TEST_RESULT ", "test_catalog": "CATALOG_TEST_RESULT ", "phase1_independent": "PHASE1_INDEPENDENT_RESULT "}
WITHOUT_SUCCESS_FIELD = {"independent_review", "test_catalog"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def product_hashes():
    paths = [ROOT / "baseline_sim.gd", ROOT / "baseline_view.gd"]
    for directory, pattern in [("combat", "*.gd"), ("data", "*.gd"), ("presentation", "*.gd"), ("game_data", "*.json"), ("benchmark", "*.gd")]:
        paths.extend((ROOT / directory).glob(pattern))
    return {str(path.relative_to(ROOT)): sha(path) for path in sorted(set(paths))}


def execute(name, negative=False):
    path = ROOT / "tests" / (name + ".gd")
    command = BASE + ["res://tests/" + name + ".gd"]
    if negative:
        command += ["--", "--prove-failure"]
    run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    label = name + ("-negative" if negative else "")
    (OUT / (label + ".stdout.log")).write_text(run.stdout, encoding="utf-8")
    (OUT / (label + ".stderr.log")).write_text(run.stderr, encoding="utf-8")
    reports = []
    for line in run.stdout.splitlines():
        prefix = PREFIXES.get(name, "")
        if prefix:
            if not line.startswith(prefix):
                continue
            line = line[len(prefix):]
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and "checks" in value and "failures" in value and ("success" in value or name in WITHOUT_SUCCESS_FIELD):
            reports.append(value)
    report = reports[-1] if len(reports) == 1 else None
    script_error = "SCRIPT ERROR" in run.stdout + run.stderr or "Parse Error" in run.stdout + run.stderr
    history = EXPECTED_HISTORY.get(name) if not negative else None
    if negative:
        accepted = run.returncode == 1 and report is not None and report["success"] is False and len(report["failures"]) == 1 and "intentional" in report["failures"][0] and '"success":true' not in run.stdout.replace(" ", "") and not script_error
        classification = "intentional failure proved"
    elif history:
        accepted = run.returncode == 1 and report is not None and report["success"] is False and report["failures"] == history and not script_error
        classification = "explicit historical catalog identity/shape difference; not a normal pass"
    else:
        accepted = run.returncode == 0 and report is not None and (report.get("success") is True or (name in WITHOUT_SUCCESS_FIELD and "success" not in report)) and report["failures"] == [] and not script_error
        classification = "normal functional pass"
    return {"name": name, "negative": negative, "command": command, "test_sha256": sha(path), "exit_code": run.returncode, "report": report, "script_error": script_error, "classification": classification, "accepted_within_declared_scope": accepted}


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    before = product_hashes()
    results = [execute(name) for name in OLD + NEW]
    results += [execute(name, True) for name in NEW + ["phase4_legacy"]]
    converter = ROOT / "tests/phase5_regression_test_converter.py"
    run = subprocess.run([sys.executable, str(converter)], cwd=ROOT, capture_output=True, text=True, timeout=30)
    (OUT / "converter.stdout.log").write_text(run.stdout, encoding="utf-8")
    (OUT / "converter.stderr.log").write_text(run.stderr, encoding="utf-8")
    converter_ok = run.returncode == 0 and "Ran 2 tests" in run.stderr and "OK" in run.stderr
    guard = json.loads((ROOT / "evidence/phase5/verification/legacy-safe-copy-manifest.json").read_text(encoding="utf-8"))
    guarded = [{**entry, "sha256_after": sha(Path(entry["path"])), "unchanged": sha(Path(entry["path"])) == entry["sha256"]} for entry in guard["past_report_guards"]]
    after = product_hashes()
    changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    summary = {"scope": "Headless functional checks, explicit historical differences and actual negative exits; no GPU/OS appearance claim", "results": results, "converter": {"test_sha256": sha(converter), "exit_code": run.returncode, "success": converter_ok}, "source_before": before, "source_after": after, "changed_during_run": changed, "historical_report_guards": guarded, "functional_outcomes_accepted": all(item["accepted_within_declared_scope"] for item in results) and converter_ok, "historical_reports_unchanged": all(item["unchanged"] for item in guarded)}
    summary["success"] = summary["functional_outcomes_accepted"] and summary["historical_reports_unchanged"] and not changed
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"directory": str(OUT), "functional_outcomes_accepted": summary["functional_outcomes_accepted"], "historical_reports_unchanged": summary["historical_reports_unchanged"], "source_changed": changed, "success": summary["success"]}, ensure_ascii=False))
    raise SystemExit(0 if summary["success"] else 1)


if __name__ == "__main__":
    main()
