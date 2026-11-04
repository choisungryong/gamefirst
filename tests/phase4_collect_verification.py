"""Assemble existing verification receipts; does not launch tests or a renderer."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFICATION = ROOT / "evidence/phase4/verification"
BUILD = ROOT / "evidence/phase4/builds/phase4-candidate-20261029-02"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest = read(BUILD / "source-manifest.json")
mismatches = [name for name, expected in manifest.items() if sha(ROOT / name) != expected.lower()]
proof = read(VERIFICATION / "freeze1-functional-proof.json")
proof_pass = all(row["exit_code"] == row["expected_exit"] and not row["has_script_error"] and
                 (not row["has_success_true"] and row["has_intentional_failure"] if row["mode"] == "negative" else row["has_success_true"])
                 for row in proof)
files = ["phase4_math.gd", "phase4_combat.gd", "phase4_catalog.gd", "phase4_scene.gd", "phase4_legacy.gd",
         "phase4_regression_phase2_scene_independent.gd", "phase4_regression_phase3_scene_independent.gd",
         "generate_phase4_math_oracle.py", "audit_phase4_runs.py", "test_phase4_audit.py",
         "phase4_independent_gpu.ps1", "phase4_exe_qa.ps1", "phase4_audit_exe_qa.py",
         "phase4_preservation_audit.py", "phase4_collect_verification.py"]
tool_hashes = {"tests/" + name: sha(ROOT / "tests" / name) for name in files}
functional_source_link = read(VERIFICATION / "candidate02-functional-source-link.json")
formal = read(VERIFICATION / "formal-three-runs-audit.json")
replay = read(ROOT / "evidence/phase4/verification-gpu-20261029-02/replay-receipt.json")
replay_audit = read(ROOT / "evidence/phase4/verification-gpu-20261029-02/independent-audit.json")
qa = read(VERIFICATION / "final-exe-qa-independent-audit.json")
success = proof_pass and functional_source_link["functional_product_files_identical"] and not mismatches and formal["success"] and replay_audit["success"] and replay["actual_exit"] == replay["audit_exit"] == 0 and not replay["source_mismatches"] and qa["success"]
report = {
    "scope": "Independent phase4 functional, synthetic 300 multi-skill performance, replay and ordinary EXE QA; root native-input acceptance remains separate",
    "verification_success": success,
    "build_record": str(BUILD / "build.json"),
    "source_manifest_sha256": sha(BUILD / "source-manifest.json"),
    "source_count": len(manifest), "current_source_mismatches": mismatches,
    "functional_counts": {"math": 343, "combat": 45, "catalog": 64, "scene": 58, "bitwise_legacy": 59},
    "five_normal_and_intentional_failure_pairs_valid": proof_pass,
    "functional_freeze_to_candidate02_link": functional_source_link,
    "legacy_regression": {"pass_counts": [40, 109, 62, 320, 203, 53, 54],
                          "historical_phase3_core": {"checks": 172, "failures": 1, "nonfailing_checks": 171, "exception": "golden fixture uses the current unchanged catalog: expected full-file hash difference after approved phase4 definitions; original failing log preserved"}},
    "formal_three_runs": formal, "independent_replay": replay_audit,
    "replay_actual_process_receipt": replay,
    "ordinary_exe_qa": qa,
    "adversarial_auditor_tests": {"count": 17, "log": str(VERIFICATION / "audit-adversarial-final.log")},
    "tools_sha256": tool_hashes,
    "open_items": ["Root native input observation and acceptance are recorded separately",
                   "Known minor auto button/mode label overlap: root observed at1440x810; fix and run during phase5 equipment UI"],
    "preservation_incident": {"report": "evidence/phase4/EVIDENCE-PRESERVATION-INCIDENT.ko.md", "phase3_note": "evidence/phase3/PRESERVATION-NOTE-20261029.ko.md", "prior_two_auxiliary_report_bytes_recovered": False},
    "limitations": ["Synthetic immortal crowd, proxy art and measurement buffers; not normal gameplay, final SACRATA quality, all-frame60FPS or D2R restoration",
                    "Historical phase3 500-actor and300-bolt stress failures remain preserved; no new phase4 pass claim for them",
                    "Two historical auxiliary scene JSON reports rewritten by test-side-effect; never cite current bytes as original approval-era reports"]}
(VERIFICATION / "verification-summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"verification_success": success, "source_count": len(manifest), "current_source_mismatches": mismatches, "functional_pairs_valid": proof_pass}))
raise SystemExit(0 if success else 1)
