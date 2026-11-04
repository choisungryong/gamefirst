"""New-path-only actual-exit collector; never writes historical QA outputs."""
from pathlib import Path
import hashlib, json, subprocess, sys, time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
GODOT = Path(r"C:\Project\rea-tools\godot-4.5.1\Godot_v4.5.1-stable_win64_console.exe")
OUT = HERE / sys.argv[1]
OUT.mkdir(exist_ok=False)
(OUT / "contract.gd.txt").write_bytes((HERE / "contract.gd").read_bytes())
cmd = [str(GODOT), "--headless", "--path", str(ROOT), "--script", str(HERE / "contract.gd")]
if "--verbose" in sys.argv:
    cmd.insert(1, "--verbose")
if "--negative" in sys.argv:
    cmd += ["--", "--prove-failure"]
started = time.time()
p = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=90)
(OUT / "stdout.txt").write_bytes(p.stdout)
(OUT / "stderr.txt").write_bytes(p.stderr)
prefix = "QUALITY04_PRESENTATION_CONTRACT "
reports = [json.loads(line[len(prefix):]) for line in p.stdout.decode("utf-8", "replace").splitlines() if line.startswith(prefix)]
record = {"command": cmd, "actual_exit": p.returncode, "elapsed_seconds": time.time()-started,
          "stdout_bytes": len(p.stdout), "stderr_bytes": len(p.stderr), "report_count": len(reports),
          "report": reports[0] if len(reports)==1 else None}
owned = ["chapter1/view/cloister_actors.gd", "chapter1/view/cloister_effects.gd", "chapter1/view/hero_occlusion_rim.gdshader", "chapter1/presentation/combat_audio.gd"]
record["source_sha256"] = {f: hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in owned}
(OUT / "execution.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"actual_exit": p.returncode, "report": record["report"], "stderr_bytes": len(p.stderr)}, ensure_ascii=False))
sys.exit(p.returncode)
