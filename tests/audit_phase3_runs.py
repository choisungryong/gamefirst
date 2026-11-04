"""Independently recompute phase3 benchmark evidence from raw CSV and PNG.

Does not launch the renderer. Integrity and the 300-actor timing goal are separate.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import struct
from pathlib import Path


def ranks(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    return {
        "min": ordered[0],
        "max": ordered[-1],
        **{f"p{p}": ordered[max(0, math.ceil(len(ordered) * p / 100) - 1)] for p in (50, 95, 99)},
    }


def audit_run(directory: Path, *, diagnostic: bool = False, goal_ms: float = 16.67) -> dict:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    report_path = directory / "summary.json"
    try:
        data = json.loads(report_path.read_text(encoding="utf-8-sig"))
        with (directory / "frames.csv").open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            raw = list(reader)
        rows = [{key: float(value) for key, value in row.items()} for row in raw]
    except (OSError, ValueError, TypeError) as error:
        return {"directory": str(directory), "integrity_pass": False, "failures": [f"Cannot read evidence: {error}"]}

    require(isinstance(data, dict), "Summary must be a JSON object")
    required_columns = {"elapsed_seconds", "frame_ms", "tick", "sim_active", "sim_alive", "render_actors", "skinned_rigs"}
    require(bool(rows) and required_columns <= rows[0].keys(), "Required raw measurement columns are missing")
    if failures:
        return {"directory": str(directory), "integrity_pass": False, "failures": failures}
    require(bool(rows), "No raw measurement frames")
    require(len(rows) == data.get("sample_count"), "Summary sample count differs from raw rows")
    require(all(math.isfinite(value) for row in rows for value in row.values()), "Raw samples contain non-finite values")
    if not rows or failures:
        return {"directory": str(directory), "integrity_pass": False, "failures": failures}

    try:
        warmup = float(data.get("warmup_seconds", -1))
        duration = float(data.get("requested_sample_seconds", -1))
    except (TypeError, ValueError):
        warmup = duration = -1
    require(math.isfinite(warmup) and math.isfinite(duration) and warmup >= 0 and duration > 0, "Invalid measurement window")
    if failures:
        return {"directory": str(directory), "integrity_pass": False, "failures": failures}
    if not diagnostic:
        require(warmup >= 10, "Final benchmark warmup is shorter than 10 seconds")
        require(duration >= 60, "Final benchmark sample is shorter than 60 seconds")

    elapsed = [row["elapsed_seconds"] for row in rows]
    frame_ms = [row["frame_ms"] for row in rows]
    explicit_window = "sample_start_elapsed" in data
    if not diagnostic:
        require(explicit_window, "Final evidence lacks the explicit fixed measurement window")
    sample_start = float(data["sample_start_elapsed"]) if explicit_window else warmup
    sample_end = elapsed[-1] if explicit_window else warmup + duration
    require(all(value > 0 for value in frame_ms), "Frame durations must be positive")
    require(all(b > a for a, b in zip(elapsed, elapsed[1:])), "Frame timestamps are not strictly increasing")
    require(sample_start >= warmup, "Measurement began before the warmup ended")
    require(all(sample_start <= value <= sample_end for value in elapsed), "Raw rows fall outside the sample window")
    require(float(data.get("wall_elapsed_seconds", 0)) >= sample_start + duration, "Run ended before the requested sample window completed")
    # The first and last sample each omit at most one boundary frame interval.
    boundary_tolerance = max(frame_ms) / 1000 + 0.005
    require(elapsed[0] - sample_start <= boundary_tolerance, "First sample begins late without a matching frame stall")
    require(sample_end - elapsed[-1] <= boundary_tolerance, "Last sample ends early without a matching frame stall")
    require(abs(elapsed[0] - float(data.get("sample_first_elapsed", -1))) <= 1e-5, "First timestamp differs from summary")
    require(abs(elapsed[-1] - float(data.get("sample_last_elapsed", -1))) <= 1e-5, "Last timestamp differs from summary")
    if explicit_window:
        require(sample_end - sample_start >= duration, "Actual raw sample interval is shorter than requested")
        require(math.isclose(float(data.get("measured_sample_seconds", -1)), sample_end - sample_start, abs_tol=2e-4), "Reported sample duration includes work outside the raw measurement interval")
        require(float(data.get("capture_elapsed", math.inf)) < sample_start, "Framebuffer readback interrupted the measurement window")

    for key in rows[0]:
        if key == "elapsed_seconds":
            continue
        actual = ranks([row[key] for row in rows])
        reported = data.get(key)
        require(isinstance(reported, dict), f"Missing summary statistics: {key}")
        if isinstance(reported, dict):
            for name, value in actual.items():
                try:
                    reported_value = float(reported[name])
                    ok = math.isfinite(reported_value) and math.isclose(reported_value, value, rel_tol=2e-5, abs_tol=2e-5)
                except (KeyError, TypeError, ValueError):
                    ok = False
                require(ok, f"Raw/statistic mismatch: {key}.{name}")
    require(data.get("stutter_gt50") == sum(value > 50 for value in frame_ms), "Stutter count differs from raw frames")

    requested = int(data.get("requested", -1))
    mode = data.get("mode")
    for key in ("sim_active", "sim_alive"):
        require(all(row[key] == requested for row in rows), f"Fixed-count stress lost active/alive entities: {key}")
    require(all(b["tick"] >= a["tick"] for a, b in zip(rows, rows[1:])), "Simulation tick went backwards")
    require(rows[-1]["tick"] > rows[0]["tick"], "Simulation did not advance during measurement")
    if mode in ("rig", "fx"):
        require(all(row["render_actors"] == requested for row in rows), "Rig/fx row omits requested actor bindings")
        # A later LOD implementation must report its split explicitly; it cannot
        # claim the requested population was all skinned when only part was.
        require(all(row["skinned_rigs"] == requested for row in rows), "Full-rig condition did not retain all requested rigs")
        if "animation_clock_progress" in rows[0]:
            require("animation_playing" in rows[0], "Missing playing-animation population")
            # Non-looping Hit/Attack clips may finish while the independent AI
            # state timer is still active; that is a retained pose, not a lost rig.
            require(all(0 < row.get("animation_playing", 0) <= requested for row in rows), "The entire animation population stopped or exceeded the actor population")
            for window in range(math.floor(sample_end - sample_start)):
                group = [row for row in rows if sample_start + window <= row["elapsed_seconds"] < sample_start + window + 1]
                require(bool(group) and sum(row["animation_clock_progress"] for row in group) > 0, f"Actual animation clocks froze in sample second {window}")
            probes = data.get("animation_probe_windows")
            if isinstance(probes, list):
                previous_end = sample_start
                previous_index = -1
                for index, probe in enumerate(probes):
                    begin = float(probe["window_start_elapsed"])
                    end = float(probe["window_end_elapsed"])
                    require(abs(begin - previous_end) <= 2e-5, f"Bone probe window {index} is not contiguous")
                    require(1 <= end - begin <= 1 + boundary_tolerance, f"Bone probe window {index} has an invalid duration")
                    raw_index = min(range(len(rows)), key=lambda number: abs(rows[number]["elapsed_seconds"] - end))
                    require(abs(rows[raw_index]["elapsed_seconds"] - end) <= 2e-5, f"Bone probe window {index} does not end on a raw frame")
                    clocks = sum(row["animation_clock_progress"] for row in rows[previous_index + 1:raw_index + 1])
                    require(clocks == probe.get("advanced_clock_count") and clocks > 0, f"Bone probe window {index} clock count differs from raw frames")
                    require(probe.get("bone_pose_changed") is True, f"Representative real bone pose froze in window {index}")
                    previous_end, previous_index = end, raw_index
                require(bool(probes) and sample_end - previous_end < 1 + boundary_tolerance, "Bone probes do not cover the complete measured window")
            elif not diagnostic:
                require(False, "Final rig evidence lacks representative bone-pose probe windows")
        elif not diagnostic:
            require(False, "Final rig evidence lacks actual animation-clock progress samples")
    if mode == "sim":
        require(all(row["render_actors"] == 0 and row["skinned_rigs"] == 0 for row in rows), "Sim-only condition retains rendered/skinned actor counts")

    require(data.get("capture_saved") is True, "Framebuffer capture was not saved")
    dimensions = (data.get("framebuffer_width"), data.get("framebuffer_height"))
    require(dimensions == (1920, 1080), "Reported framebuffer is not actual 1920x1080")
    try:
        prefix = (directory / "frame.png").read_bytes()[:24]
        require(prefix[:8] == b"\x89PNG\r\n\x1a\n", "Capture is not a PNG")
        actual_dimensions = struct.unpack(">II", prefix[16:24])
        require(actual_dimensions == dimensions == (1920, 1080), "PNG dimensions do not match the 1080p report")
    except (OSError, struct.error):
        require(False, "Cannot inspect saved PNG dimensions")
    require(bool(data.get("adapter")), "GPU adapter is missing; headless is not GPU evidence")
    require(data.get("display_server", "").lower() != "headless", "Headless run cannot satisfy GPU evidence")
    require(data.get("rendering_method") in ("gl_compatibility", "forward_plus", "mobile"), "Unknown rendering method")
    require(data.get("max_fps") == 0, "Benchmark has an FPS cap")
    require(data.get("vsync_mode") == 0, "Benchmark VSync is enabled")

    if data.get("workload") == "skill" and mode == "fx":
        try:
            project = Path(__file__).resolve().parents[1]
            catalog = json.loads((project / "game_data" / "catalog.json").read_text(encoding="utf-8-sig"))
            skill = next(item for item in catalog["skills"] if item["id"] == catalog["experiment"]["skill_id"])
            projectile = next(item for item in catalog["projectiles"] if item["id"] == skill["projectile_id"])
            hz = int(catalog["simulation_hz"])
            lifetime = round(projectile["lifetime_seconds"] * hz)
            cycle = int(skill["cycle_ticks"])
            theoretical = math.ceil(lifetime / cycle)
            budget = data["skill_budget"]
            require(budget["cycle_ticks"] == cycle and budget["projectile_life_ticks"] == lifetime and budget["theoretical_max_simultaneous_bolts"] == theoretical and budget["mana_cost_raw"] == skill["cost"]["raw"], "Reported skill budget differs from the actual catalog")
            require(data.get("fixture_bolts") == 0, "Actual skill workload injects fixture bolts")
            require(max(row["bolts"] for row in rows) <= theoretical, "Observed skill bolts exceed the catalog lifetime/cycle budget")
            events = data["sample_event_counts"]
            expected_casts = (sample_end - sample_start) * hz / cycle
            require(abs(events.get("cast_start", 0) - expected_casts) <= 2, "Actual cast frequency differs from the catalog cycle")
            require(abs(events.get("release", 0) - expected_casts) <= 2, "Actual release frequency differs from the catalog cycle")
            require(0 < events.get("hit", 0) <= events.get("release", 0) + theoretical, "Skill workload lacks plausible real hit events")
            require(data.get("cast_proxy_count") == events.get("cast_start"), "Cast proxy count differs from actual cast events")
            require(max(row["fx_particles"] for row in rows) > 0, "Skill workload has no actual FX activity")
            require(data.get("configuration", {}).get("mana_refilled_every_tick") is True, "Sustained-cast mana refill is not declared")
        except (OSError, ValueError, TypeError, KeyError, StopIteration) as error:
            require(False, f"Cannot independently verify actual skill budget: {error}")
    elif not diagnostic and mode == "fx":
        require(data.get("workload") == "projectile_stress", "Final FX evidence does not declare its workload")

    for key, limit in (("history", 4096), ("actor_pool", 512), ("projectile_pool", 512), ("particle_pool", 256), ("fx_particles", 256)):
        if key in rows[0]:
            require(max(row[key] for row in rows) <= limit, f"Game state exceeded its declared cap: {key}")

    if data.get("source_hashes_basis", "").startswith("embedded"):
        try:
            project = Path(__file__).resolve().parents[1]
            source_manifest = json.loads((project / "evidence" / "phase3" / "source-manifest.json").read_text(encoding="utf-8-sig"))
            expected_sources = {entry["path"].replace("\\", "/"): entry["sha256"].lower() for entry in source_manifest}
            metadata_hash = expected_sources.pop("game_data/build_info.json")
            actual_sources = {key.replace("\\", "/"): value.lower() for key, value in data["source_hashes"].items()}
            require(actual_sources == expected_sources, "Embedded pre-export source map differs from the accepted phase3 source manifest")
            require(data.get("embedded_source_manifest_sha256", "").lower() == metadata_hash, "Embedded metadata hash differs from the accepted source manifest")
            if (directory / "launch.json").is_file():
                launch = json.loads((directory / "launch.json").read_text(encoding="utf-8-sig"))
                require(launch.get("embedded_preexport_manifest_sha256", "").lower() == metadata_hash, "External launch metadata differs from runtime metadata")
                accepted_build = json.loads((project / "evidence" / "phase3" / "final-build.json").read_text(encoding="utf-8-sig"))
                require(launch.get("exe_sha256", "").lower() == accepted_build["exe_sha256"].lower(), "External launch executable hash differs from the accepted final build")
            elif not diagnostic:
                require(False, "Final release evidence lacks its external launch record")
        except (OSError, ValueError, TypeError, KeyError) as error:
            require(False, f"Cannot verify exported source provenance: {error}")
    elif not diagnostic:
        require(False, "Final release evidence lacks an embedded pre-export source manifest")

    if explicit_window:
        measured = sample_end - sample_start
        start_tick = int(data.get("sample_start_tick", -1))
        end_tick = int(data.get("sample_end_tick", -1))
        require(end_tick == int(rows[-1]["tick"]), "Final simulation tick differs from the final raw frame")
        require(data.get("time_scale") == 1, "Simulation time scale changed")
        require(abs((end_tick - start_tick) / 60 - measured) <= 0.1, "Simulation did not preserve 60Hz progress over wall time")
        try:
            with (directory / "physics.csv").open(encoding="utf-8-sig", newline="") as handle:
                physics = [{key: float(value) for key, value in row.items()} for row in csv.DictReader(handle)]
            require(len(physics) == data.get("physics_sample_count") == end_tick - start_tick, "Per-tick raw count differs from the simulation interval")
            require(bool(physics) and all(row["tick"] == start_tick + index + 1 for index, row in enumerate(physics)), "Per-tick raw sequence is missing or duplicated")
            require(sum(row["physics_ticks_in_frame"] for row in rows) == len(physics), "Frame CPU aggregation omits or duplicates physics callbacks")
            require(math.isclose(sum(row["sim_frame_ms"] for row in rows), sum(row["sim_tick_ms"] for row in physics), abs_tol=0.002), "Frame simulation-time sums disagree with individual physics samples")
            if physics:
                for key in physics[0]:
                    if key in ("elapsed_seconds", "tick"):
                        continue
                    expected_statistics = ranks([row[key] for row in physics])
                    for name, value in expected_statistics.items():
                        require(math.isclose(float(data.get(key, {}).get(name, math.inf)), value, rel_tol=2e-5, abs_tol=2e-5), f"Per-tick statistic mismatch: {key}.{name}")
        except (OSError, ValueError, TypeError, KeyError) as error:
            require(False, f"Cannot verify per-tick raw evidence: {error}")

    measured_span = elapsed[-1] - elapsed[0]
    tick_rate = (rows[-1]["tick"] - rows[0]["tick"]) / measured_span if measured_span > 0 else 0
    percentiles = ranks(frame_ms)
    return {
        "directory": str(directory),
        "integrity_pass": not failures,
        "failures": failures,
        "requested": requested,
        "mode": mode,
        "rendering_method": data.get("rendering_method"),
        "frames": len(rows),
        "measured_timestamp_span_seconds": measured_span,
        "physics_ticks_per_wall_second": tick_rate,
        "frame_ms": percentiles,
        "goal_threshold_ms": goal_ms,
        "p95_goal_pass": percentiles["p95"] <= goal_ms,
        "goal_scope": "timing threshold only; does not establish art, game balance or original-game equivalence",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directories", nargs="+", type=Path)
    parser.add_argument("--diagnostic", action="store_true", help="Allow explicitly labelled short diagnostic runs")
    parser.add_argument("--require-goal", action="store_true", help="Also fail if the p95 timing threshold is missed")
    parser.add_argument("--goal-ms", type=float, default=16.67)
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    if not math.isfinite(options.goal_ms) or options.goal_ms < 0:
        parser.error("--goal-ms must be finite and nonnegative")
    results = [audit_run(path, diagnostic=options.diagnostic, goal_ms=options.goal_ms) for path in options.directories]
    success = all(result["integrity_pass"] and (not options.require_goal or result.get("p95_goal_pass", False)) for result in results)
    output = {"scope": "independent raw evidence audit; integrity and timing goals are separate", "success": success, "runs": results}
    if options.output:
        options.output.parent.mkdir(parents=True, exist_ok=True)
        options.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
