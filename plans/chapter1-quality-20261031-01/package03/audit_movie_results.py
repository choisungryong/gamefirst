"""Compare actual normal-driver terminal state, excluding presentation timing."""
from pathlib import Path
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("quality03_package", HERE/"package_quality03.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
results = {}
for variant in ("old", "new"):
    proof = HERE/"movies"/(variant+"-20261101-01")
    execution = p.read(proof/"movie-execution.json")
    assert execution["actual_exit"] == 0
    rows = [json.loads(line.split("CHAPTER1_RUNTIME_RESULT ",1)[1]) for line in execution["stdout"].splitlines()
            if "CHAPTER1_RUNTIME_RESULT " in line]
    assert rows
    def gameplay(row):
        return {key:value for key,value in row.items() if key not in ("frame_p95_ms","frame_samples","scope")}
    assert all(gameplay(row) == gameplay(rows[0]) for row in rows)
    results[variant] = {"raw_results":rows,"gameplay":gameplay(rows[0]),"stderr":execution["stderr"]}
assert results["old"]["gameplay"] == results["new"]["gameplay"]
gameplay_result = results["new"]["gameplay"]
assert gameplay_result["mode"] == "victory" and gameplay_result["elapsed"] == 78.15
assert gameplay_result["kills"] == 813
assert gameplay_result["growth"]["ranks"] == {"chapter1.skill.ember":4,"chapter1.skill.frost":3,"chapter1.skill.arc":3}
build = p.read(p.PROOF/"build.json")
assert p.sha(build["exe"]) == build["sha256"]
p.write(HERE/"movies/comparison-20261101-01/terminal-state-comparison.json", {
    "actual_engine_exits":{"old":0,"new":0},"gameplay_terminal_state_equal":True,"results":results,
    "excluded_presentation_fields":["frame_p95_ms","frame_samples","scope"],
    "new_exe_sha256":p.sha(build["exe"]),"preservation":p.preservation(),
    "scope":"Same deterministic core/input terminal-state comparison; fixed30FPS timings are not performance evidence; new forced-exit resource warning remains open"})
print(json.dumps({"success":True,"gameplay_terminal_state_equal":True,"mode":"victory","elapsed":78.15,"kills":813}))
