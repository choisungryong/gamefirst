"""Replay core04 checks into a NEW evidence directory; never overwrite history."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
GODOT = r"C:\Project\rea-tools\godot-4.5.1\Godot_v4.5.1-stable_win64_console.exe"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    prefix = "res://" + HERE.relative_to(ROOT).as_posix() + "/"
    cases = [
        ("parse", ["--check-only", "--script", "res://chapter1/core/combat_run.gd"], 0),
        ("semantic", ["--script", prefix + "semantic_regression.gd"], 0),
        ("semantic-negative", ["--script", prefix + "semantic_regression.gd", "--", "--prove-failure"], 1),
        ("crowd", ["--script", prefix + "test_crowd.gd"], 0),
        ("crowd-negative", ["--script", prefix + "test_crowd.gd", "--", "--prove-failure"], 1),
        ("corner", ["--script", prefix + "corner_diagnostic.gd"], 0),
        ("normal-pilot", ["--script", prefix + "normal_pilot.gd", "--", "--output=" + str(output / "normal-results.json")], None),
    ]
    digest = hashlib.sha256((ROOT / "chapter1/core/combat_run.gd").read_bytes()).hexdigest()
    for name, arguments, expected in cases:
        command = [GODOT, "--headless", "--path", str(ROOT)] + arguments
        begin = time.monotonic()
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=180)
        record = dict(command=command, cwd=str(ROOT), actual_exit=completed.returncode,
                      stdout=completed.stdout, stderr=completed.stderr,
                      wall_seconds=time.monotonic() - begin, combat_run_sha256_at_start=digest)
        (output / (name + "-execution.json")).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        print(name, "actual_exit", completed.returncode, flush=True)
        if expected is not None and completed.returncode != expected:
            raise SystemExit("Unexpected actual exit: " + name)
        if completed.stderr:
            raise SystemExit("Unexpected stderr: " + name)
        if name == "normal-pilot":
            results = json.loads((output / "normal-results.json").read_text(encoding="utf-8"))
            if len(results["cases"]) != 6 or any(row.get("mode") not in ("victory", "defeat") for row in results["cases"]):
                raise SystemExit("Pilot did not finish six real terminal cases")
            # A real defeat deliberately retains actual_exit1/success:false.
            if completed.returncode != (0 if results["success"] else 1):
                raise SystemExit("Pilot actual exit disagrees with raw result")
    current = hashlib.sha256((ROOT / "chapter1/core/combat_run.gd").read_bytes()).hexdigest()
    if current != digest:
        raise SystemExit("Core source changed during verification")


if __name__ == "__main__":
    main()
