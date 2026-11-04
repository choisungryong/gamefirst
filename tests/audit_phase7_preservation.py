"""Final read-only source/archive/native guards; unique output is mandatory."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
def read(path): return json.loads(path.read_text(encoding="utf-8-sig"))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-no-game", action="store_true")
    args = parser.parse_args()
    assert not args.output.exists(), "Preserve prior audit"
    build_root = ROOT / "evidence/phase7/builds/phase7-candidate-20261030-01"
    build = read(build_root / "build.json")
    original = read(build_root / "source-manifest.json")
    staging = read(build_root / "staging-manifest.json")
    result = {"scope": "Current workspace, original snapshot and transformed staging are different pinned scopes; no executable source-byte recovery claim", "original_count": len(original), "staging_count": len(staging), "original_mismatches": [], "staging_mismatches": [], "phase6_archive_mismatches": [], "guard_mismatches": []}
    for name, expected in original.items():
        if sha(ROOT / name) != expected or sha(build_root / "source" / name) != expected: result["original_mismatches"].append(name)
    for name, expected in staging.items():
        if sha(Path(build["stage"]) / name) != expected: result["staging_mismatches"].append(name)
    result["exe_sha256"] = sha(Path(build["exe"]))
    result["exe_unchanged"] = result["exe_sha256"] == build["exe_sha256"]
    package = read(build_root / "pck-audit.json")
    result["pck_audit_entries"] = package["entry_count"]
    result["pck_audit_link_valid"] = package["success"] and package["forbidden_matches"] == [] and package["exe_sha256"] == result["exe_sha256"]
    old_root = ROOT / "evidence/phase6/builds/phase6-candidate-20261030-01"
    old = read(old_root / "source-manifest.json")
    result["phase6_archive_count"] = len(old)
    for name, expected in old.items():
        if sha(old_root / "source" / name) != expected: result["phase6_archive_mismatches"].append(name)
    result["phase6_exe_unchanged"] = sha(ROOT / "builds/phase6/phase6-candidate-20261030-01/D2RCombatBaseline-phase6.exe") == "8f787d8d043951e0d500743f38c3df1348dfadb99a08f04365b36310ba38ab89"
    checks = read(ROOT / "evidence/phase7/verification/functional-20261030-185348-704358/summary.json")["historical_and_user_guards"]
    result["guard_count"] = len(checks)
    for row in checks:
        path = Path(row["path"])
        if (sha(path) if path.exists() else None) != row["sha256_before"]: result["guard_mismatches"].append(str(path))
    equipment = Path(r"C:\Users\twins\AppData\Roaming\Godot\app_userdata\D2R Combat Baseline\equipment-v1.json")
    progress = equipment.with_name("progress-v1.json")
    result["native_equipment_sha256"] = sha(equipment)
    result["native_equipment_unchanged"] = result["native_equipment_sha256"] == "b376f88d6db4c443332908f5cf09860a4eda24701cbefb25c9cbd8289e202353"
    result["native_progress_absent"] = not progress.exists()
    command = ["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(AshenCloister|D2RCombatBaseline|Godot)' } | Select-Object ProcessId,Name | ConvertTo-Json -Compress"]
    query = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    result["process_query_exit"] = query.returncode
    result["game_processes"] = json.loads(query.stdout) if query.stdout.strip() else []
    result["success"] = not any(result[name] for name in ("original_mismatches", "staging_mismatches", "phase6_archive_mismatches", "guard_mismatches")) and all(result[name] for name in ("exe_unchanged", "pck_audit_link_valid", "phase6_exe_unchanged", "native_equipment_unchanged", "native_progress_absent")) and query.returncode == 0 and (not args.require_no_game or not result["game_processes"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["success"] else 1)


if __name__ == "__main__": main()
