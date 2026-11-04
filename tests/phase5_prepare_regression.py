"""Prepare legacy scene copies with phase5-only report output.

This script does not execute Godot or regenerate any historical expectation.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/phase5/verification"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    mappings = [
        ("phase2_scene_independent.gd", "res://evidence/phase3/verification/scene-regression-report", "res://evidence/phase5/verification/legacy-scene-regression-report"),
        ("phase3_scene_independent.gd", "res://evidence/phase3/verification/mixed-corpse-report", "res://evidence/phase5/verification/legacy-mixed-corpse-report"),
    ]
    copies = []
    for name, old, new in mappings:
        source = ROOT / "tests" / name
        target = ROOT / "tests" / ("phase5_regression_" + name)
        original = source.read_text(encoding="utf-8")
        assert original.count(old) == 1, (name, "expected exactly one output literal")
        expected = original.replace(old, new)
        if target.exists():
            assert target.read_text(encoding="utf-8") == expected, "Refusing to overwrite differing regression copy"
        else:
            target.write_text(expected, encoding="utf-8", newline="")
        assert target.read_text(encoding="utf-8").replace(new, old) == original
        copies.append({"source": str(source), "source_sha256": sha(source), "copy": str(target), "copy_sha256": sha(target), "only_replacement": {"from": old, "to": new}})
    guards = []
    for phase in ("phase3", "phase4"):
        for path in sorted((ROOT / "evidence" / phase).rglob("scene-run.json")):
            guards.append({"path": str(path), "sha256": sha(path), "size": path.stat().st_size})
    report = {"scope": "Output path copies only; historical fixture/source bytes are never regenerated", "copies": copies, "past_report_guards": guards}
    destination = OUT / "legacy-safe-copy-manifest.json"
    if destination.exists():
        previous = json.loads(destination.read_text(encoding="utf-8"))
        assert previous == report, "Prior safety manifest differs; preserve it and investigate"
    else:
        destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    converter_source = ROOT / "tests/test_converter.py"
    converter_copy = ROOT / "tests/phase5_regression_test_converter.py"
    converter_original = converter_source.read_text(encoding="utf-8")
    converter_old = "ROOT / 'evidence' / 'phase1'"
    converter_new = "ROOT / 'evidence' / 'phase5' / 'verification'"
    assert converter_original.count(converter_old) == 2
    converter_expected = converter_original.replace(converter_old, converter_new)
    if converter_copy.exists():
        assert converter_copy.read_text(encoding="utf-8") == converter_expected
    else:
        converter_copy.write_text(converter_expected, encoding="utf-8", newline="")
    converter_manifest = {"source": str(converter_source), "source_sha256": sha(converter_source), "copy": str(converter_copy), "copy_sha256": sha(converter_copy), "only_replacement": {"from": converter_old, "to": converter_new, "count": 2}}
    converter_destination = OUT / "converter-safe-copy-manifest.json"
    if converter_destination.exists():
        assert json.loads(converter_destination.read_text(encoding="utf-8")) == converter_manifest
    else:
        converter_destination.write_text(json.dumps(converter_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"scene_copies": len(copies), "converter_copies": 1, "guarded_historical_reports": len(guards), "success": True}))


if __name__ == "__main__":
    main()
