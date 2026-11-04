"""Root-controlled actual packaged native QA. No injected UI/input/cheats.

Run only after root allocates GPU and explicitly requests launch. The helper waits
for the user/root to close the game through its UI and records its actual exit.
It never terminates the game, sends keys, or silently switches to an autopilot.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("quality03_package", HERE/"package_quality03.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
assert len(sys.argv) == 3 and sys.argv[1] == "launch", "Usage: launch_native03.py launch UNIQUE_RUN_ID"
run_id = sys.argv[2]
assert p.re.fullmatch(r"[a-z0-9-]+", run_id)
proof = HERE.parent/"native-runtime-03"/run_id
p.fresh_dir(proof)
build = p.read(p.PROOF/"build.json")
exe = Path(build["exe"])
assert p.sha(exe) == build["sha256"]
captures = exe.parent/"qa-captures"/run_id
p.fresh_dir(captures)
command = [str(exe),"--resolution","1440x810","--log-file",str(proof/"godot.log"),"--",
           "--chapter1-capture-dir="+str(captures)]
started = datetime.now(timezone.utc).isoformat()
before = p.preservation()
with (proof/"stdout.log").open("xb") as stdout, (proof/"stderr.log").open("xb") as stderr:
    process = subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,close_fds=True)
    p.write(proof/"LAUNCH.json",{"pid":process.pid,"command":command,"started_utc":started,
        "exe_sha256":p.sha(exe),"captures":str(captures),"no_pilot":True,"no_autostart":True,
        "focus_behavior":"normal auto-pause on focus loss","input_log":"omitted: exported QA input-log allowlist does not include qa-captures",
        "scope":"Actual native manual QA launcher only; root operates UI with approved computer-use tool"})
    print(json.dumps({"pid":process.pid,"proof":str(proof),"manual_default":True}),flush=True)
    actual_exit = process.wait()
ended = datetime.now(timezone.utc).isoformat()
copied = proof/"captures"
copied.mkdir()
capture_manifest = {}
for image in sorted(captures.glob("*.png")):
    target = copied/image.name
    assert not target.exists()
    shutil.copy2(image,target)
    assert p.sha(image) == p.sha(target)
    capture_manifest[image.name] = {"sha256":p.sha(image),"bytes":image.stat().st_size}
after = p.preservation()
assert before == after
assert p.sha(exe) == build["sha256"]
logs = {name:p.sha(proof/name) for name in ("stdout.log","stderr.log","godot.log") if (proof/name).is_file()}
p.write(proof/"EXECUTION.json",{"command":command,"pid":process.pid,"actual_exit":actual_exit,
    "started_utc":started,"ended_utc":ended,"exe_sha256":p.sha(exe),"captures":capture_manifest,
    "logs_sha256":logs,"preservation_before":before,"preservation_after":after,
    "scope":"Actual native manual-session raw evidence; root observations separately determine tested interactions; no audio hearing or quality approval inferred"})
print(json.dumps({"actual_exit":actual_exit,"proof":str(proof),"capture_count":len(capture_manifest)}),flush=True)
sys.exit(actual_exit)
