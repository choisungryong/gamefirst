"""Independent phase7 tests; phase6 outputs and user files are read-only guards."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ENGINE = Path(r"C:\Project\rea-tools\godot-4.5.1\Godot_v4.5.1-stable_win64_console.exe")
OUT = ROOT / "evidence/phase7/verification" / ("functional-"+dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
RECIPES = ["phase6_regression_phase2_scene_independent", "phase6_regression_phase3_scene_independent", "phase6_regression_phase5_sim_storage", "phase6_progression_independent", "phase6_scene_independent"]
LEGACY = ["test_sim", "independent_review", "test_catalog", "phase1_independent", "phase2_independent", "phase7_safe_phase6_regression_phase2_scene_independent", "phase3_independent", "phase7_safe_phase6_regression_phase3_scene_independent", "phase4_math", "phase4_combat", "phase4_catalog", "phase4_scene", "phase4_legacy", "phase5_equipment", "phase7_safe_phase6_regression_phase5_sim_storage", "phase5_skill_catalog", "phase7_safe_phase6_progression_independent", "phase7_safe_phase6_scene_independent"]
NEW = ["phase7_run_independent", "phase7_presentation_independent"]
RELOCATED = {}
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def products():
    paths = [ROOT/p for p in ["baseline_sim.gd", "baseline_view.gd", "expedition_view.gd", "Baseline.tscn", "Expedition.tscn", "project.godot"] if (ROOT/p).exists()]
    for directory, pattern in [("combat", "*.gd"), ("data", "*.gd"), ("presentation", "*.gd"), ("run", "*.gd"), ("game_data", "*.json"), ("benchmark", "*.gd")]: paths.extend((ROOT/directory).glob(pattern))
    paths.extend((ROOT/"assets/expedition").rglob("*.wav"))
    return {str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))}
def prepare():
    copies = []
    for name in RECIPES:
        original = ROOT/"tests"/(name+".gd")
        copy = ROOT/"tests"/("phase7_safe_"+name+".gd")
        data = original.read_text(encoding="utf-8").replace("res://evidence/phase6/", "res://evidence/phase7/")
        if copy.exists(): assert copy.read_text(encoding="utf-8") == data, "refuse to overwrite differing safety copy"
        else: copy.write_text(data,encoding="utf-8")
        # Each execution gets its own output prefix. Keep the prior safe copies and
        # every earlier phase7 report intact, even when this runner is repeated.
        run_copy = OUT/"safe-sources"/copy.name
        run_copy.parent.mkdir(exist_ok=True)
        run_prefix = "res://"+OUT.relative_to(ROOT).as_posix()+"/legacy-output/"
        run_copy.write_text(data.replace("res://evidence/phase7/",run_prefix),encoding="utf-8")
        RELOCATED[copy.stem] = run_copy
        copies.append({"source":str(original),"source_sha256":sha(original),"copy":str(copy),"copy_sha256":sha(copy),"run_copy":str(run_copy),"run_copy_sha256":sha(run_copy),"change":"phase6 evidence prefix to phase7 canonical copy, then unique per-execution output prefix"})
    return copies
def guarded():
    old = json.loads((ROOT/"evidence/phase6/verification/legacy-safe-copy-manifest.json").read_text(encoding="utf-8"))["guards"]
    targets = {Path(r["path"]):r["sha256"] for r in old if r["exists"]}
    targets.update({p:sha(p) for p in (ROOT/"evidence/phase6").rglob("*") if p.is_file()})
    targets.update({p:sha(p) for p in (ROOT/"evidence/phase7/verification").rglob("*") if p.is_file() and not p.is_relative_to(OUT)})
    targets[Path(r"C:\Users\twins\AppData\Roaming\Godot\app_userdata\D2R Combat Baseline\progress-v1.json")] = None
    return targets
def execute(name, negative=False):
    source = RELOCATED.get(name,ROOT/"tests"/(name+".gd"))
    snapshot = OUT/"test-sources"/source.name
    snapshot.parent.mkdir(exist_ok=True)
    if snapshot.exists(): assert snapshot.read_bytes()==source.read_bytes(), "test source changed between positive/negative runs"
    else: snapshot.write_bytes(source.read_bytes())
    command = [str(ENGINE),"--headless","--path",str(ROOT),"--script","res://"+source.relative_to(ROOT).as_posix()]
    if negative: command += ["--","--prove-failure"]
    run = subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=120)
    label = name+("-negative" if negative else "")
    (OUT/(label+".stdout.log")).write_text(run.stdout,encoding="utf-8")
    (OUT/(label+".stderr.log")).write_text(run.stderr,encoding="utf-8")
    reports = []
    for line in run.stdout.splitlines():
        idx = line.find("{")
        if idx < 0: continue
        try: report = json.loads(line[idx:])
        except json.JSONDecodeError: continue
        if isinstance(report,dict) and "checks" in report and "failures" in report: reports.append(report)
    report = reports[-1] if len(reports)==1 else None
    errors = "SCRIPT ERROR" in run.stdout+run.stderr or "Parse Error" in run.stdout+run.stderr
    historical = {"phase3_independent":["golden fixture uses the current unchanged catalog"],"phase4_catalog":["three skill and ten stat definitions"]}.get(name)
    if negative:
        accepted = run.returncode==1 and report is not None and report.get("success") is False and len(report["failures"])==1 and "intentional" in report["failures"][0] and '"success":true' not in run.stdout.replace(" ","") and not errors
        classification = "intentional actual exit1"
    elif historical:
        accepted = run.returncode==1 and report is not None and report["failures"]==historical and not errors
        classification = "historical catalog identity/shape difference; not normal pass"
    else:
        accepted = run.returncode==0 and report is not None and not report["failures"] and not errors
        classification = "normal pass" if accepted else "unresolved failure"
    return {"name":name,"negative":negative,"command":command,"exit_code":run.returncode,"report":report,"script_error":errors,"classification":classification,"accepted":accepted,"test_sha256":sha(source),"test_snapshot":str(snapshot)}
def main():
    OUT.mkdir(parents=True,exist_ok=False)
    copies = prepare()
    guards = guarded()
    assert all((sha(p) if p.exists() else None)==h for p,h in guards.items()), "historical/user guard changed before execution"
    before = products()
    names = NEW if "--new-only" in sys.argv else LEGACY+NEW
    if "--scene" in sys.argv:
        names = names+["phase7_scene_independent"]
    results = [execute(name) for name in names]
    negative = NEW+(["phase7_scene_independent"] if "--scene" in sys.argv else [])
    results += [execute(name,True) for name in negative]
    after = products()
    changed = [p for p in before.keys()|after.keys() if before.get(p)!=after.get(p)]
    rows = [{"path":str(p),"sha256_before":h,"sha256_after":sha(p) if p.exists() else None,"unchanged":(sha(p) if p.exists() else None)==h} for p,h in guards.items()]
    summary = {"scope":"Independent phase7 headless/controller/scene and baseline-mode regressions; no GPU/OS/final-art/fun claim","results":results,"safe_copies":copies,"source_before":before,"source_after":after,"changed_during_run":changed,"historical_and_user_guards":rows,"success":all(r["accepted"] for r in results) and all(r["unchanged"] for r in rows) and not changed}
    (OUT/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"directory":str(OUT),"success":summary["success"],"failed":[r["name"] for r in results if not r["accepted"]],"changed_during_run":changed},ensure_ascii=False))
    raise SystemExit(0 if summary["success"] else 1)
if __name__=="__main__": main()
