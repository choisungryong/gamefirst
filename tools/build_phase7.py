"""Immutable expedition-only staging/export; never modifies the working product.

PCK layout verification follows official Godot 4.5.1 core/io/file_access_pack.cpp.
https://github.com/godotengine/godot/blob/4.5.1-stable/core/io/file_access_pack.cpp
Export preset selection follows official editor/export/editor_export.cpp.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ENGINE = Path(r"C:\Project\rea-tools\godot-4.5.1\Godot_v4.5.1-stable_win64_console.exe")
STAGES = Path(r"C:\Project\game-research\implementation-staging")
LEDGER = ROOT / "evidence/phase7/runtime-polish-20261030-01/ASSET-LEDGER.json"
FORBIDDEN = ("firebolt-sheet", "original-cast-strip", "firebolt-decoded", "baseline_view", "Baseline.tscn", "benchmark/", "tests/", "evidence/", "research/", "tools/")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def checked_relative(value):
    value = value.replace("\\", "/")
    assert not value.startswith(("/", "res://")) and ":" not in value and ".." not in value.split("/"), value
    return value


def runtime_paths():
    # Explicit script closure excludes diagnostic views and their research atlas.
    paths = {"Expedition.tscn", "expedition_view.gd", "baseline_sim.gd", "project.godot", "export_presets.cfg", "game_data/build_info.json"}
    paths.update(p.relative_to(ROOT).as_posix() for folder in ("data", "combat", "run") for p in (ROOT / folder).glob("*.gd"))
    paths.update("presentation/" + name + ".gd" for name in ("input_controller", "actor_registry", "skinned_mesh_batch", "static_batch", "equipment_presenter", "expedition_world", "expedition_hud", "expedition_effects", "expedition_audio", "expedition_loot"))
    paths.update("game_data/" + name + ".json" for name in ("catalog", "equipment", "loot"))
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    for row in ledger["records"]:
        if row["path"].startswith("assets/"):
            value = checked_relative(row["path"])
            assert sha(ROOT / value) == row["sha256"], "Asset ledger stale: " + value
            paths.add(value)
            if row.get("license", "").startswith("assets/"):
                paths.add(checked_relative(row["license"]))
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT / "assets/licenses").glob("*.txt"))
    assert any(p.endswith("ambience.wav") for p in paths)
    assert not any(any(term.lower() in p.lower() for term in FORBIDDEN) for p in paths)
    return sorted(paths)


def prepare(build_id):
    assert re.fullmatch(r"phase7-[A-Za-z0-9-]+", build_id), "Invalid build id"
    output = ROOT / "builds/phase7" / build_id
    evidence = ROOT / "evidence/phase7/builds" / build_id
    stage = STAGES / build_id
    assert not any(p.exists() for p in (output, evidence, stage)), "Preserve prior candidate; choose a new ID"
    for p in (output, evidence, stage):
        p.mkdir(parents=True)
    paths = runtime_paths()
    source_hashes = {p: sha(ROOT / p) for p in paths}
    sidecar_hashes = {}
    for p in paths:
        for target_root in (evidence / "source", stage):
            target = target_root / p
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / p, target)
        # Import settings keep GLB/texture and WAV behavior; imported cache is rebuilt.
        for sidecar in (ROOT / (p + ".import"), ROOT / (p + ".uid")):
            if sidecar.is_file():
                relative = sidecar.relative_to(ROOT)
                sidecar_hashes[relative.as_posix()] = sha(sidecar)
                for target_root in (evidence / "source", stage):
                    shutil.copy2(sidecar, target_root / relative)
    project = (stage / "project.godot").read_text(encoding="utf-8")
    assert project.count('run/main_scene="res://Baseline.tscn"') == 1
    (stage / "project.godot").write_text(project.replace('run/main_scene="res://Baseline.tscn"', 'run/main_scene="res://Expedition.tscn"'), encoding="utf-8")
    preset = (stage / "export_presets.cfg").read_text(encoding="utf-8")
    preset = preset.replace('name="Windows Desktop"', 'name="Expedition Windows"').replace('export_filter="all_resources"', 'export_filter="selected_resources"')
    resource_paths = ["res://" + p for p in paths if p.endswith((".gd", ".tscn", ".glb", ".png", ".wav"))]
    preset = preset.replace('export_filter="selected_resources"', 'export_filter="selected_resources"\nexport_files=PackedStringArray(' + ', '.join(json.dumps(p) for p in resource_paths) + ')')
    (stage / "export_presets.cfg").write_text(preset, encoding="utf-8")
    stage_hashes = {p: sha(stage / p) for p in paths if p != "game_data/build_info.json"}
    metadata = {"build_id": build_id, "basis": "staging source hashes before export; original workspace hashes are a separate manifest", "source_hashes": stage_hashes}
    write(stage / "game_data/build_info.json", metadata)
    stage_hashes["game_data/build_info.json"] = sha(stage / "game_data/build_info.json")
    write(evidence / "source-manifest.json", source_hashes)
    write(evidence / "staging-manifest.json", stage_hashes)
    write(evidence / "source-import-sidecars.json", sidecar_hashes)
    write(evidence / "packaging-plan.json", {"build_id": build_id, "stage": str(stage), "output": str(output), "source_hashes": source_hashes, "staging_hashes": stage_hashes, "sidecar_hashes": sidecar_hashes, "transformed": [p for p in paths if source_hashes[p] != stage_hashes[p]], "forbidden": FORBIDDEN, "metadata_basis": metadata["basis"], "asset_ledger_sha256": sha(LEDGER)})
    return evidence, stage, output


def pck_entries(executable):
    # Godot V2/V3 unencrypted directory, including the executable trailer format.
    blob = executable.read_bytes()
    assert blob[-4:] == b"GDPC", "Missing embedded PCK trailer"
    size = struct.unpack_from("<Q", blob, len(blob) - 12)[0]
    start = len(blob) - 12 - size
    assert blob[start:start + 4] == b"GDPC", "Invalid PCK start"
    version, major, minor, patch, flags = struct.unpack_from("<IIIII", blob, start + 4)
    assert version in (2, 3) and (major, minor) == (4, 5) and flags in (0, 2), "Unsupported PCK format"
    file_base = struct.unpack_from("<Q", blob, start + 24)[0]
    if version == 3 or flags & 2:
        file_base += start
    at = start + struct.unpack_from("<Q", blob, start + 32)[0] if version == 3 else start + 96
    count = struct.unpack_from("<I", blob, at)[0]
    at += 4
    assert 0 < count < 100000
    entries = []
    for _ in range(count):
        length = struct.unpack_from("<I", blob, at)[0]
        at += 4
        assert 0 < length < 65536
        path = blob[at:at + length].rstrip(b"\0").decode("utf-8")
        at += length
        offset, length = struct.unpack_from("<QQ", blob, at)
        at += 16
        digest = blob[at:at + 16].hex()
        at += 16
        entry_flags = struct.unpack_from("<I", blob, at)[0]
        at += 4
        assert entry_flags == 0, "Encrypted/removal entry unsupported"
        data = blob[file_base + offset:file_base + offset + length]
        assert len(data) == length and hashlib.md5(data).hexdigest() == digest, "PCK payload checksum mismatch: " + path
        entries.append({"path": path, "size": length, "md5": digest, "sha256": hashlib.sha256(data).hexdigest()})
    assert len({e["path"] for e in entries}) == len(entries)
    return {"format_version": version, "engine_version": [major, minor, patch], "entry_count": count, "entries": entries}


def audit(executable, evidence):
    report = pck_entries(executable)
    paths = [e["path"].removeprefix("res://") for e in report["entries"]]
    violations = [p for p in paths if any(term.lower() in p.lower() for term in FORBIDDEN)]
    # Import hashes hide file names, so import sidecars and .remap paths also matter.
    for expected in ("Expedition.tscn.remap", "expedition_view.gd.remap", "game_data/build_info.json", "game_data/catalog.json", "game_data/equipment.json", "game_data/loot.json"):
        assert expected in paths, "Required runtime entry missing: " + expected
    for expected in ("assets/actors/Mage.glb.import", "assets/actors/Skeleton_Minion.glb.import"):
        assert expected in paths, "Missing dynamic model: " + expected
    plan = json.loads((evidence / "packaging-plan.json").read_text(encoding="utf-8"))
    for source in plan["source_hashes"]:
        if source.startswith("assets/"):
            expected = source + ".import" if source.endswith((".glb", ".png", ".wav")) else source
            assert expected in paths, "Dynamic asset or license omitted: " + source
    actual_metadata = next(e["sha256"] for e in report["entries"] if e["path"].removeprefix("res://") == "game_data/build_info.json")
    assert actual_metadata == plan["staging_hashes"]["game_data/build_info.json"], "Packaged metadata differs from staging"
    assert not violations, "Forbidden packaged files: " + repr(violations)
    report.update({"exe_sha256": sha(executable), "forbidden_matches": violations, "success": True, "scope": "Complete embedded PCK directory and payload checksums, not execution/quality approval"})
    write(evidence / "pck-audit.json", report)
    return report


def run_export(evidence, stage, output):
    plan = json.loads((evidence / "packaging-plan.json").read_text(encoding="utf-8"))
    for name, digest in plan["source_hashes"].items():
        assert sha(ROOT / name) == digest, "Workspace changed after preparation: " + name
    for name, digest in plan["sidecar_hashes"].items():
        assert sha(ROOT / name) == digest and sha(stage / name) == digest, "Import settings changed after preparation: " + name
    for name, digest in plan["staging_hashes"].items():
        assert sha(stage / name) == digest, "Staging changed: " + name
    executable = output / "AshenCloister-phase7.exe"
    assert not executable.exists(), "Do not overwrite a candidate"
    commands = [[str(ENGINE), "--headless", "--path", str(stage), "--editor", "--import"], [str(ENGINE), "--headless", "--path", str(stage), "--export-release", "Expedition Windows", str(executable)]]
    for index, command in enumerate(commands):
        with (evidence / ("import.log" if index == 0 else "export.log")).open("wb") as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
        write(evidence / ("import-exit.json" if index == 0 else "export-exit.json"), {"command": command, "exit_code": result.returncode})
        assert result.returncode == 0, "Godot import/export failed; inspect preserved log"
    for name, digest in plan["source_hashes"].items():
        assert sha(ROOT / name) == digest, "Workspace changed during export: " + name
    for name, digest in plan["staging_hashes"].items():
        assert sha(stage / name) == digest, "Staging source changed during export: " + name
    write(evidence / "staging-import-sidecars-after.json", {name: sha(stage / name) for name in plan["sidecar_hashes"]})
    for name, digest in plan["sidecar_hashes"].items():
        assert sha(ROOT / name) == digest, "Workspace import settings changed during export: " + name
    package = audit(executable, evidence)
    build = {"build_id": plan["build_id"], "exe": str(executable), "exe_sha256": sha(executable), "source_manifest": str(evidence / "source-manifest.json"), "staging_manifest": str(evidence / "staging-manifest.json"), "source_count": len(plan["source_hashes"]), "metadata_sha256": plan["staging_hashes"]["game_data/build_info.json"], "entrypoint": "res://Expedition.tscn", "stage": str(stage), "export_exit": 0, "pck_entries": package["entry_count"], "scope": "Expedition candidate only; GPU/OS/performance/quality approval separate"}
    write(evidence / "build.json", build)
    print(json.dumps(build, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-id", required=True)
    parser.add_argument("--export", action="store_true")
    parser.add_argument("--resume-prepared", action="store_true")
    args = parser.parse_args()
    if args.resume_prepared:
        assert args.export
        evidence = ROOT / "evidence/phase7/builds" / checked_relative(args.build_id)
        plan = json.loads((evidence / "packaging-plan.json").read_text(encoding="utf-8"))
        stage, output = Path(plan["stage"]), Path(plan["output"])
    else:
        evidence, stage, output = prepare(args.build_id)
    if args.export:
        run_export(evidence, stage, output)
    else:
        print(json.dumps({"prepared": True, "evidence": str(evidence), "stage": str(stage), "exported": False}))


if __name__ == "__main__":
    main()
