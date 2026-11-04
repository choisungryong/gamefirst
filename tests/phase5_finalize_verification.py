"""Collect preserved phase5 evidence without launching or modifying product code."""
from pathlib import Path
import datetime as dt
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/phase5/verification"
BUILD = ROOT / "evidence/phase5/builds/phase5-candidate-20261029-01"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    destination = OUT / "verification-summary.json"
    if destination.exists():
        raise SystemExit("Preserve prior summary")
    manifest = read(BUILD / "source-manifest.json")
    build = read(BUILD / "build.json")
    products = [{"path": key, "expected_sha256": value, "current_sha256": sha(ROOT / key), "frozen_sha256": sha(BUILD / "source" / key)} for key, value in manifest.items()]
    product_match = all(row["expected_sha256"] == row["current_sha256"] == row["frozen_sha256"] for row in products)
    metadata = read(BUILD / "source/game_data/build_info.json")
    metadata_match = metadata["source_hashes"] == {key: value for key, value in manifest.items() if key != "game_data/build_info.json"}
    functional_path = OUT / "functional-20261030-072021-717501/summary.json"
    functional = read(functional_path)
    guard = read(OUT / "legacy-safe-copy-manifest.json")
    guarded = [{**item, "sha256_final": sha(Path(item["path"])), "unchanged": sha(Path(item["path"])) == item["sha256"]} for item in guard["past_report_guards"]]
    formal_path = OUT / "formal-three-runs-independent-audit-20261030.json"
    formal = read(formal_path)
    replay_path = ROOT / "evidence/phase5/verification-gpu-20261030-01/replay-receipt.json"
    replay = read(replay_path)
    replay_audit = read(replay_path.parent / "independent-audit.json")
    qa_path = OUT / "final-exe-equipment-qa-independent-audit-20261030.json"
    qa = read(qa_path)
    smoke = read(OUT / "gpu-smoke-independent-audit-final-20261030.json")
    adverse_log = OUT / "audit-adversaries-20261030.stderr.log"
    adversaries_ok = "Ran 30 tests" in adverse_log.read_text() and adverse_log.read_text().rstrip().endswith("OK")
    evidence = [functional_path, formal_path, replay_path, replay_path.parent / "independent-audit.json", qa_path, OUT / "gpu-smoke-independent-audit-final-20261030.json", OUT / "frozen-fingerprint-oracle-20261030.json", adverse_log]
    scripts = [ROOT / "tests" / name for name in ("phase5_run_functional.py", "audit_phase5_runs.py", "test_phase5_audit.py", "phase5_fingerprint_oracle.gd", "phase5_independent_gpu.ps1", "phase5_exported_qa.gd", "phase5_exported_qa.ps1", "audit_phase5_exported_qa.py", "phase5_finalize_verification.py")]
    source_reference = read(Path(r"C:\Project\game-research\implementation-backups\phase5-before-20261029-072409\manifest.json"))
    reference_hashes = {row["path"].replace("\\", "/"): row["sha256"].lower() for row in source_reference}
    original_auditors = [{"path": key, "sha256": sha(ROOT / key), "backup_sha256": reference_hashes.get(key)} for key in ("tests/audit_phase4_runs.py", "tests/test_phase4_audit.py")]
    prior_auditors_unchanged = all(row["sha256"] == row["backup_sha256"] for row in original_auditors)
    scope_ok = functional["success"] and product_match and metadata_match and all(item["unchanged"] for item in guarded) and formal["success"] and all(run["formal_goal_pass"] for run in formal["runs"]) and replay["actual_exit"] == replay["audit_exit"] == replay["stderr_bytes"] == replay["game_processes_remaining"] == 0 and replay["source_mismatches"] == [] and replay_audit["success"] and qa["success"] and adversaries_ok and prior_auditors_unchanged
    result = {"client_date": "2026-10-30", "timezone": "Asia/Seoul", "checked_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "scope": "Independent functional, formal equipped GPU raw audit, one replay and two external exported-scene QA resolutions. Root OS input/art/fun approval is separate.", "verification_success": bool(scope_ok), "exe_sha256": sha(Path(build["exe"])), "accepted_exe_matches": sha(Path(build["exe"])) == build["exe_sha256"], "source_count": len(products), "products": products, "metadata_match": metadata_match, "functional_summary": str(functional_path), "functional_results": [{key: item[key] for key in ("name", "negative", "exit_code", "classification", "accepted_within_declared_scope")} | {"checks": item["report"]["checks"]} for item in functional["results"]], "historical_report_guards": guarded, "original_phase4_auditors": original_auditors, "formal_runs": formal["runs"], "independent_replay": replay_audit["runs"], "external_qa": qa, "smoke_not_formal": smoke["runs"], "audit_adversaries": {"tests": 30, "observed_process_exit": 0, "log": str(adverse_log), "success": adversaries_ok}, "evidence_hashes": {str(path.relative_to(ROOT)): sha(path) for path in evidence}, "verification_script_hashes": {str(path.relative_to(ROOT)): sha(path) for path in scripts}, "open_items_owned_by_root": ["Actual OS keyboard/mouse equipment save/load/close observations", "Overall phase acceptance and next-phase decision"]}
    result["verification_success"] = result["verification_success"] and result["accepted_exe_matches"]
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(destination), "verification_success": result["verification_success"], "source_count": len(products), "source_mismatches": [row["path"] for row in products if row["expected_sha256"] != row["current_sha256"] or row["expected_sha256"] != row["frozen_sha256"]], "historical_reports_unchanged": all(item["unchanged"] for item in guarded), "prior_auditors_unchanged": prior_auditors_unchanged}))
    raise SystemExit(0 if result["verification_success"] else 1)


if __name__ == "__main__":
    main()
