"""Independent phase6 execution; immutable history guards, unique output logs."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ENGINE = Path(r"C:\Project\rea-tools\godot-4.5.1\Godot_v4.5.1-stable_win64_console.exe")
OUT = ROOT / "evidence/phase6/verification-independent" / ("functional-"+dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
LEGACY = ["test_sim", "independent_review", "test_catalog", "phase1_independent", "phase2_independent", "phase6_regression_phase2_scene_independent", "phase3_independent", "phase6_regression_phase3_scene_independent", "phase4_math", "phase4_combat", "phase4_catalog", "phase4_scene", "phase4_legacy", "phase5_equipment", "phase6_regression_phase5_sim_storage", "phase5_skill_catalog"]
NEW = ["phase6_progression_independent", "phase6_scene_independent"]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def products():
    paths = [ROOT / "baseline_sim.gd", ROOT / "baseline_view.gd"]
    for directory, pattern in [("combat", "*.gd"), ("data", "*.gd"), ("presentation", "*.gd"), ("game_data", "*.json"), ("benchmark", "*.gd")]:
        paths.extend((ROOT / directory).glob(pattern))
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(paths))}

def execute(name, negative=False):
    command = [str(ENGINE), "--headless", "--path", str(ROOT), "--script", "res://tests/"+name+".gd"]
    if negative: command += ["--", "--prove-failure"]
    run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90)
    label = name+("-negative" if negative else "")
    (OUT / (label+".stdout.log")).write_text(run.stdout, encoding="utf-8")
    (OUT / (label+".stderr.log")).write_text(run.stderr, encoding="utf-8")
    reports = []
    for line in run.stdout.splitlines():
        index = line.find("{")
        if index == -1: continue
        try: report = json.loads(line[index:])
        except json.JSONDecodeError: continue
        if isinstance(report, dict) and "checks" in report and "failures" in report: reports.append(report)
    report = reports[-1] if len(reports) == 1 else None
    errors = "SCRIPT ERROR" in run.stdout+run.stderr or "Parse Error" in run.stdout+run.stderr
    history = {"phase3_independent":["golden fixture uses the current unchanged catalog"],"phase4_catalog":["three skill and ten stat definitions"]}.get(name)
    if negative:
        accepted = run.returncode == 1 and report is not None and report.get("success") is False and len(report["failures"]) == 1 and "intentional" in report["failures"][0] and '"success":true' not in run.stdout.replace(" ", "") and not errors
        classification = "intentional actual exit1"
    elif history:
        accepted = run.returncode == 1 and report is not None and report.get("failures") == history and not errors
        classification = "historical definition identity/shape difference; not pass"
    else:
        accepted = run.returncode == 0 and report is not None and not report["failures"] and not errors
        classification = "normal pass" if accepted else "unresolved failure"
    return {"name":name,"negative":negative,"command":command,"exit_code":run.returncode,"script_error":errors,"test_sha256":sha(ROOT / "tests" / (name+".gd")),"report":report,"classification":classification,"accepted":accepted}

def main():
    OUT.mkdir(parents=True, exist_ok=False)
    guard = json.loads((ROOT / "evidence/phase6/verification/legacy-safe-copy-manifest.json").read_text(encoding="utf-8"))["guards"]
    assert all(Path(row["path"]).exists() == row["exists"] and (not row["exists"] or sha(Path(row["path"])) == row["sha256"]) for row in guard), "historical guard changed before run"
    user_progress = Path(r"C:\Users\twins\AppData\Roaming\Godot\app_userdata\D2R Combat Baseline\progress-v1.json")
    progress_before = sha(user_progress) if user_progress.exists() else None
    before = products()
    selected = NEW if "--new-only" in sys.argv else LEGACY+NEW
    results = [execute(name) for name in selected]
    results += [execute(name, True) for name in NEW]
    checked = [{**row,"unchanged":Path(row["path"]).exists() == row["exists"] and (not row["exists"] or sha(Path(row["path"])) == row["sha256"])} for row in guard]
    after = products()
    progress_after = sha(user_progress) if user_progress.exists() else None
    changed = [name for name in before.keys() | after.keys() if before.get(name) != after.get(name)]
    summary = {"results":results,"source_before":before,"source_after":after,"changed_during_run":changed,"historical_guards":checked,"user_progress_before":progress_before,"user_progress_after":progress_after,"excluded_unsafe_historical_scene":"phase6_regression_phase5_scene overrides equipment methods only; phase6 UI uses progress API, so executing historical copy could write actual user progress save","success":all(r["accepted"] for r in results) and all(r["unchanged"] for r in checked) and not changed and progress_before == progress_after}
    (OUT / "summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"directory":str(OUT),"success":summary["success"],"failed":[r["name"] for r in results if not r["accepted"]],"source_changed":changed},ensure_ascii=False))
    raise SystemExit(0 if summary["success"] else 1)

if __name__ == "__main__": main()
