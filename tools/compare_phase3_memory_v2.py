"""Small process-clock matched comparison; does not certify leak absence."""
import csv
import json
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parents[1] / "evidence" / "phase3"
RETAINED = EVIDENCE / "release-soak-20261028" / "forward_plus-skill-n300-soak600"
CONTROL = EVIDENCE / "memory-control-v2-300-20261028"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def window(directory):
    with (directory / "process-memory.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = [{key: float(value) for key, value in row.items()} for row in csv.DictReader(stream)]
    if rows[-1]["elapsed_seconds"] < 300:
        raise ValueError("The 300-second comparison is not complete")
    selected = [row for row in rows if 60 <= row["elapsed_seconds"] <= 300]
    result = {"clock": "runner process elapsed, not benchmark sample elapsed", "requested_window_seconds": [60, 300], "first_elapsed": selected[0]["elapsed_seconds"], "last_elapsed": selected[-1]["elapsed_seconds"], "observations": len(selected)}
    xs = [row["elapsed_seconds"] for row in selected]
    mean_x = sum(xs) / len(xs)
    for key in ("private_bytes", "working_set_bytes"):
        ys = [row[key] for row in selected]
        mean_y = sum(ys) / len(ys)
        slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / sum((x - mean_x) ** 2 for x in xs)
        result[key] = {"first": ys[0], "last": ys[-1], "delta_MiB": (ys[-1] - ys[0]) / 1048576, "least_squares_KiB_per_second": slope / 1024, "minimum": min(ys), "maximum": max(ys)}
    return result


def main():
    execution = load(CONTROL / "execution.json")
    control = load(CONTROL / "control-report.json")
    if not execution["success"] or not execution["exe_unchanged"] or not control["clear_state_unchanged"] or control.get("control_version") != 2 or control.get("failed_gate_predicates") or (CONTROL / "summary.json").exists():
        raise ValueError("The control execution/protocol did not pass")
    retained = window(RETAINED)
    reclaimed = window(CONTROL)
    result = {"scope": "Non-performance attribution diagnostic; report differences without claiming all allocation sources or zero leaks", "matched_clock": "each runner's process elapsed60..300s, startup/report phases excluded; initial absolute allocation not assumed equal", "retained_directory": str(RETAINED), "control_directory": str(CONTROL), "retained": retained, "reclaimed_every_second": reclaimed, "control_actual_sample_seconds": control["actual_sample_seconds"], "control_physics_seconds": control["physics_seconds"], "clear_count": control["clear_count"], "removed_frame_rows": control["frame_rows_removed"], "removed_tick_rows": control["tick_rows_removed"], "maximum_retained_frame_rows": control["maximum_retained_frame_rows"], "maximum_retained_tick_rows": control["maximum_retained_tick_rows"], "control_state_checks": {"all_clear_unchanged": control["clear_state_unchanged"], "all_alive300": all(row["alive"] == 300 for row in control["observations"]), "all_rigs300": all(row["rigs"] == 300 for row in control["observations"]), "all_clock_bone_windows_progressed": all(row["advanced_clock_count"] > 0 and row["bone_pose_changed"] for row in control["animation_probe_windows"])}, "unresolved": "Variant/container/allocator/driver/observer costs are not separately attributed; this finite comparison does not certify universal leak absence"}
    result["control_state_checks"]["within_window_same_probe_motion_and_clock"] = control["predicates"]["same_probe_within_window_pose_and_ap_clock"]
    result["control_state_checks"].pop("all_clock_bone_windows_progressed")
    result["control_state_checks"]["global_clock_windows_advanced"] = all(row["advanced_clock_count"] > 0 for row in control["animation_probe_windows"])
    result["legacy_endpoint_predicate_informational"] = control["predicates"]["legacy_endpoint_bone_comparison"]
    result["observer_extra_retention"] = "V2 retains at most1501 scalar probe records and300 window records, plus one previous41-bone pose; observer/allocator overhead not separately attributed"
    (EVIDENCE / "memory-control-v2-comparison.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
