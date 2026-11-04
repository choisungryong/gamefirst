"""Independent raw audit of phase7 candidate QA; never rewrites its source run."""
from pathlib import Path
import argparse
import array
import csv
import hashlib
import json
import math
import struct
import wave

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "evidence/phase7/builds/phase7-candidate-20261030-01"


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding="utf-8-sig"))
def require(value, message):
    if not value: raise ValueError(message)
def quantile(values, probability): return sorted(values)[max(0, math.ceil(len(values) * probability) - 1)]


def audit(directory):
    launch, receipt = read(directory / "launch.json"), read(directory / "receipt.json")
    report = read(directory / "case/summary.json")
    build = read(BUILD / "build.json")
    require(sha(Path(build["exe"])) == build["exe_sha256"] == launch["exe_sha256"] == receipt["exe_sha256"], "Candidate executable pin")
    require(launch["metadata_sha256"] == report["candidate_metadata_sha256"] == build["metadata_sha256"], "Candidate metadata pin")
    require(sha(directory / "external-harness.gd") == launch["external_script_sha256"] == report["external_script_sha256"], "Executed harness snapshot pin")
    require(receipt["actual_exit"] == 0 and receipt["report_success"] and report["success"] and not report["failures"], "Actual successful exit and report")
    require(receipt["native_guards_unchanged"] and launch["native_guards_before"] == receipt["native_guards_after"], "Native user file guards")
    require(receipt["source_mismatches"] == [] and receipt["external_harness_matches"] and receipt["stderr_bytes"] == 0 and (directory / "stderr.log").stat().st_size == 0, "Source/harness/stderr receipt")
    for target, expected in launch["native_guards_before"].items():
        path = Path(target)
        require((sha(path) if path.exists() else None) == expected, "Current native file guard " + target)
    original = read(BUILD / "source-manifest.json")
    stage = read(BUILD / "staging-manifest.json")
    for name, expected in original.items():
        require(sha(ROOT / name) == sha(BUILD / "source" / name) == expected, "Original/source snapshot pin " + name)
    for name, expected in stage.items():
        require(sha(Path(build["stage"]) / name) == expected, "Staging pin " + name)
    require(report["renderer"] == "forward_plus" and "RTX 2070 SUPER" in report["hardware"], "Renderer/hardware identity")
    dimensions = tuple(report["framebuffer"])
    require(dimensions in ((1440, 810), (1920, 1080)), "Requested framebuffer dimensions")
    for capture in report["captures"]:
        image = Path(capture["path"])
        require(image.parent.resolve() == (directory / "case").resolve(), "Capture location")
        data = image.read_bytes()
        require(data[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", data[16:24]) == dimensions == tuple(capture["size"]), "Actual PNG dimensions")
        require(sha(image) == capture["sha256"], "PNG pin")
    result = {"directory": str(directory), "mode": report["mode"], "checks": report["checks"], "captures": len(report["captures"]), "framebuffer": list(dimensions), "integrity_success": True, "limitations": ["Automated external SceneTree is separate from OS input", "Source remap/pin does not recover original GDScript bytes from executable", "Audio waveform presence is not listening approval", "Synthetic stress is separate from normal play", "Timing is observer-inclusive; soak samples are one frame per second, not a full-frame latency distribution"]}
    frames = directory / "case/frames.csv"
    if frames.exists():
        rows = list(csv.DictReader(frames.open(encoding="utf-8")))
        require(bool(rows), "Nonempty timing samples")
        columns = ("elapsed_seconds", "frame_ms", "run_tick", "sim_tick", "life", "mana_raw", "kills", "alive", "actors", "created_actors", "nodes", "transients", "projectiles", "loot", "audio_played")
        values = [{key: float(row[key]) for key in columns} for row in rows]
        require(all(math.isfinite(value) for row in values for value in row.values()), "Finite samples")
        require(all(row["frame_ms"] > 0 for row in values), "Positive frame durations")
        require(all(b["elapsed_seconds"] > a["elapsed_seconds"] for a, b in zip(values, values[1:])), "Monotone wall-clock samples")
        require(all(row["transients"] <= 160 and row["projectiles"] <= 128 and row["loot"] <= 32 for row in values), "Per-sample bounded visual pools")
        metrics = report.get("timing", report.get("metrics", {}))
        durations = [row["frame_ms"] for row in values]
        calculated = {"count": len(rows), "sample_seconds": values[-1]["elapsed_seconds"] - values[0]["elapsed_seconds"], "p50": quantile(durations, .5), "p95": quantile(durations, .95), "p99": quantile(durations, .99), "worst": max(durations), "frames_over_50ms": sum(v > 50 for v in durations)}
        for key, expected in calculated.items():
            require(key in metrics and math.isclose(float(metrics[key]), expected, abs_tol=.002, rel_tol=1e-6), "Raw timing recomputation " + key)
        result["recomputed"] = calculated
        result["ranges"] = {key: [min(row[key] for row in values), max(row[key] for row in values)] for key in columns if key not in ("elapsed_seconds", "frame_ms")}
        mode = report["mode"]
        if mode == "stress":
            require(dimensions == (1920, 1080) and calculated["sample_seconds"] >= 59.9 and len(rows) > 1000, "Formal stress sample duration/framebuffer")
            # The fixture replenishes at tick start, then ordinary enemy hits can
            # lower life before the rendered sample. Exact equality is invalid.
            harness = (directory / "external-harness.gd").read_text(encoding="utf-8")
            require("view.sim.life=1000000.0" in harness and all(row["alive"] == 300 and 900000 <= row["life"] <= 1000000 for row in values), "Explicit synthetic 300/high-life fixture")
            result["p95_goal_pass"] = calculated["p95"] <= 16.67
            result["all_frames_60fps"] = calculated["worst"] <= 1000 / 60
        elif mode == "pilot":
            require(report["run_results"], "Pilot terminal outcome")
            require(all(0 <= row["life"] <= 50 for row in values), "Pilot retains finite ordinary health")
            require(all(snapshot["state"] in ("victory", "defeat", "timeout") for snapshot in report["run_results"]), "Recognized outcome")
            result["outcomes"] = [{"state": s["state"], "elapsed_ticks": s["elapsed_ticks"], "elite_defeated": s["elite_defeated"]} for s in report["run_results"]]
        elif mode == "soak":
            require(calculated["sample_seconds"] >= 599 and len(rows) <= 602, "Ten-minute bounded observer rows")
            result["outcomes"] = [s["state"] for s in report["run_results"]]
    audio = directory / "case/mixed-audio.wav"
    if audio.exists():
        with wave.open(str(audio), "rb") as recording:
            require(recording.getsampwidth() == 2 and recording.getframerate() > 0, "PCM16 recording")
            count, channels, rate = recording.getnframes(), recording.getnchannels(), recording.getframerate()
            energy, samples, peak = 0, 0, 0
            while True:
                data = recording.readframes(32768)
                if not data: break
                values_ = array.array("h", data)
                energy += sum(int(v) * int(v) for v in values_)
                samples += len(values_)
                peak = max(peak, max(abs(v) for v in values_))
            require(peak > 0 and energy > 0, "Recorded non-silent mixed waveform")
            result["audio"] = {"sha256": sha(audio), "seconds": count / rate, "channels": channels, "sample_rate": rate, "peak_pcm16": peak, "rms_pcm16": math.sqrt(energy / samples), "listened": False}
    memory = directory / "process-memory.csv"
    if memory.exists():
        memory_rows = list(csv.DictReader(memory.open(encoding="utf-8-sig")))
        result["memory_csv_columns"] = list(memory_rows[0]) if memory_rows else []
        result["memory_rows"] = len(memory_rows)
        if memory_rows:
            sampled = [{key: float(row[key]) for key in ("elapsed_seconds", "private_bytes", "working_set_bytes")} for row in memory_rows]
            require(all(math.isfinite(v) and v >= 0 for row in sampled for v in row.values()), "Finite nonnegative process memory")
            require(all(b["elapsed_seconds"] > a["elapsed_seconds"] for a, b in zip(sampled, sampled[1:])), "Monotone process memory samples")
            late = [row for row in sampled if row["elapsed_seconds"] >= 60]
            if late:
                result["memory_after_60_seconds"] = {"first_seconds": late[0]["elapsed_seconds"], "last_seconds": late[-1]["elapsed_seconds"], "private_delta_mib": (late[-1]["private_bytes"] - late[0]["private_bytes"]) / 1048576, "working_set_delta_mib": (late[-1]["working_set_bytes"] - late[0]["working_set_bytes"]) / 1048576, "private_range_mib": [min(row["private_bytes"] for row in late) / 1048576, max(row["private_bytes"] for row in late) / 1048576], "working_set_range_mib": [min(row["working_set_bytes"] for row in late) / 1048576, max(row["working_set_bytes"] for row in late) / 1048576]}
        result["memory_limitation"] = "Process private/RSS includes engine/allocator/driver/observer; growth alone neither proves nor disproves a leak"
    result["success"] = result.get("p95_goal_pass", True)
    if not result["success"]:
        result["failure"] = "Raw integrity passed but formal stress p95 exceeds 16.67ms goal"
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "Preserve prior audit output")
    snapshot = args.output.with_suffix(".auditor.py")
    require(not snapshot.exists(), "Preserve prior auditor source snapshot")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    snapshot.write_bytes(Path(__file__).read_bytes())
    try:
        result = audit(args.directory.resolve())
    except Exception as error:
        result = {"success": False, "failure": str(error), "directory": str(args.directory)}
    result["auditor_snapshot"] = str(snapshot)
    result["auditor_sha256"] = sha(snapshot)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("success", "mode", "failure", "recomputed") if key in result}, ensure_ascii=False))
    raise SystemExit(0 if result["success"] else 1)


if __name__ == "__main__": main()
