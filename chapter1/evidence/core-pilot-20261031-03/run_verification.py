"""Capture actual subprocess commands, stdout/stderr and exit codes without overwrites."""
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent
GODOT = r"C:\Project\rea-tools\godot-4.5.1\Godot_v4.5.1-stable_win64_console.exe"
BASE = [GODOT, "--headless", "--path", str(ROOT), "--quit-after", "2"]
CASES = [
    ("parse", ["--check-only", "--script", "res://chapter1/core/combat_run.gd"]),
    ("functional-positive", ["--script", "res://chapter1/tests/test_combat_run.gd"]),
    ("functional-negative", ["--script", "res://chapter1/tests/test_combat_run.gd", "--", "--prove-failure"]),
    ("normal-pilot", ["--script", "res://chapter1/tests/pilot_combat_run.gd", "--", "--output=" + str(OUT / "results.json")]),
]
for name, args in CASES:
    destination = OUT / (name + "-execution.json")
    if destination.exists():
        raise SystemExit("Refusing to overwrite " + str(destination))
    command = BASE + args
    completed = subprocess.run(command, cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True)
    record = {"command": command, "cwd": str(ROOT), "actual_exit": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}
    destination.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(name, "actual_exit", completed.returncode, flush=True)
    if name != "normal-pilot":
        print(completed.stdout.strip(), flush=True)
    if completed.stderr:
        print(completed.stderr.strip(), flush=True)
    expected = 1 if name == "functional-negative" else 0
    if completed.returncode != expected or "SCRIPT ERROR" in completed.stderr:
        raise SystemExit("Unexpected result in " + name)
