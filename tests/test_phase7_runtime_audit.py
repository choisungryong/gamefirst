"""In-memory counterexamples; no QA/historical file is edited."""
import copy
import importlib.util
import json
from pathlib import Path
import sys

spec = importlib.util.spec_from_file_location("phase7_auditor", Path(__file__).with_name("audit_phase7_runtime.py"))
auditor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auditor)
directory = auditor.ROOT / "evidence/phase7/runtime-features-1920-20261030-01"
original = auditor.read
cases = [
    ("actual process failure", "receipt.json", lambda d: d.update(actual_exit=1)),
    ("stderr false green", "receipt.json", lambda d: d.update(stderr_bytes=3)),
    ("candidate pin mismatch", "launch.json", lambda d: d.update(exe_sha256="0" * 64)),
    ("metadata mismatch", "summary.json", lambda d: d.update(candidate_metadata_sha256="0" * 64)),
    ("harness mismatch", "summary.json", lambda d: d.update(external_script_sha256="0" * 64)),
    ("incorrect framebuffer claim", "summary.json", lambda d: d.update(framebuffer=[1920, 1079])),
    ("modified screenshot", "summary.json", lambda d: d["captures"][0].update(sha256="0" * 64)),
    ("source changed during run", "receipt.json", lambda d: d.update(source_mismatches=["expedition_view.gd"])),
]
results = []
for name, filename, mutate in cases:
    def altered(path, filename=filename, mutate=mutate):
        value = original(path)
        if path.name == filename:
            value = copy.deepcopy(value)
            mutate(value)
        return value
    auditor.read = altered
    try:
        auditor.audit(directory)
        results.append({"case": name, "rejected": False})
    except ValueError as error:
        results.append({"case": name, "rejected": True, "reason": str(error)})
auditor.read = original
result = {"success": all(row["rejected"] for row in results), "scope": "In-memory malformed receipt/report claims only; original run files remain read-only", "results": results}
print(json.dumps(result, ensure_ascii=False))
raise SystemExit(0 if result["success"] else 1)
