"""Adversarial proof that phase4 raw audit rejects altered evidence.

Uses preserved short GPU smoke as input; no renderer is launched.
"""
import csv
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from audit_phase4_runs import audit_run

PROJECT = Path(__file__).resolve().parents[1]
SMOKE = PROJECT / "evidence/phase4/gpu-smoke-20261029-01/forward-plus-multi-skill-n300-r1"
BUILD = PROJECT / "evidence/phase4/builds/phase4-smoke-20261029-01"


class Phase4AuditAdversaries(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="phase4-audit-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name) / "evidence"
        shutil.copytree(SMOKE, self.directory)
        self.manifest_path = BUILD / "source-manifest.json"

    def audit(self, diagnostic=True):
        return audit_run(self.directory, diagnostic=diagnostic,
                         source_manifest_path=self.manifest_path,
                         build_record_path=BUILD / "build.json")

    def summary(self):
        return json.loads((self.directory / "summary.json").read_text(encoding="utf-8-sig"))

    def write_summary(self, value):
        (self.directory / "summary.json").write_text(json.dumps(value), encoding="utf-8")

    def events(self):
        return [json.loads(line) for line in (self.directory / "skill-events.jsonl").read_text().splitlines()]

    def write_events(self, entries):
        (self.directory / "skill-events.jsonl").write_text("\n".join(json.dumps(row) for row in entries) + "\n")

    def rejects(self, fragment):
        result = self.audit()
        self.assertFalse(result["integrity_pass"])
        self.assertTrue(any(fragment in item for item in result["failures"]), result["failures"])

    def test_original_diagnostic_integrity(self):
        self.assertTrue(self.audit()["integrity_pass"])

    def test_mutable_catalog_is_not_consulted(self):
        original_read = Path.read_text

        def guarded_read(path, *args, **kwargs):
            if path == PROJECT / "game_data/catalog.json":
                raise AssertionError("Mutable project catalog was consulted")
            return original_read(path, *args, **kwargs)

        with patch.object(Path, "read_text", guarded_read):
            self.assertTrue(self.audit()["integrity_pass"])

    def test_frozen_catalog_hash_mismatch_rejected(self):
        frozen = Path(self.temporary.name) / "frozen"
        (frozen / "source/game_data").mkdir(parents=True)
        shutil.copy2(BUILD / "source-manifest.json", frozen / "source-manifest.json")
        (frozen / "source/game_data/catalog.json").write_text("{}")
        self.manifest_path = frozen / "source-manifest.json"
        self.rejects("Frozen catalog bytes differ")

    def test_short_smoke_cannot_be_formal(self):
        result = self.audit(diagnostic=False)
        self.assertFalse(result["integrity_pass"])
        self.assertIn("Final benchmark sample is shorter than 60 seconds", result["failures"])

    def test_missing_event_rejected(self):
        entries = self.events()
        entries.pop(next(i for i, row in enumerate(entries) if row["event"]["kind"] == "hit"))
        self.write_events(entries)
        self.rejects("Raw skill event log differs")

    def test_duplicate_release_rejected(self):
        entries = self.events()
        index = next(i for i, row in enumerate(entries) if row["event"]["kind"] == "release")
        entries.insert(index, entries[index])
        self.write_events(entries)
        self.rejects("Duplicate release")

    def test_damage_outside_definition_rejected(self):
        entries = self.events()
        next(row["event"] for row in entries if row["event"]["kind"] == "hit")["damage_raw"] = 1
        self.write_events(entries)
        self.rejects("damage outside")

    def test_status_wrong_expiry_rejected(self):
        entries = self.events()
        next(row["event"] for row in entries if row["event"]["kind"] == "status_applied")["until_tick"] += 1
        self.write_events(entries)
        self.rejects("chill strength/expiry")

    def test_duplicate_instant_handle_rejected(self):
        entries = self.events()
        event = next(row["event"] for row in entries if row["event"]["kind"] == "skill_effect")
        event["targets"].append(event["targets"][0])
        self.write_events(entries)
        self.rejects("duplicates/exceeds target")

    def test_unknown_skill_rejected(self):
        entries = self.events()
        next(row["event"] for row in entries if row["event"]["kind"] == "hit")["skill_id"] = "skill.unknown"
        self.write_events(entries)
        self.rejects("unknown skill")

    def test_unfired_hit_shot_rejected(self):
        entries = self.events()
        next(row["event"] for row in entries if row["event"]["kind"] == "hit")["shot"] = 1000000
        self.write_events(entries)
        self.rejects("unobserved release shot")

    def test_release_shot_and_hit_renumbered_rejected(self):
        entries = self.events()
        event = next(row["event"] for row in entries if row["event"]["kind"] == "release")
        previous_shot = event["shot"]
        for entry in entries:
            if entry["event"].get("shot") == previous_shot:
                entry["event"]["shot"] = 1000000
        self.write_events(entries)
        self.rejects("not contiguous")

    def test_context_error_rejected(self):
        data = self.summary()
        data["combat_errors"] = ["lost context"]
        self.write_summary(data)
        self.rejects("context failures")

    def test_visual_capacity_rejected(self):
        data = self.summary()
        data["skill_fx_pool"]["created"] = 65
        self.write_summary(data)
        self.rejects("visual pool cap")

    def test_embedded_map_forgery_rejected(self):
        data = self.summary()
        data["source_hashes"]["combat/stat_block.gd"] = "0" * 64
        self.write_summary(data)
        self.rejects("source map differs")

    def test_event_tick_outside_window_rejected(self):
        entries = self.events()
        entries[-1]["event"]["tick"] = 1000000
        self.write_events(entries)
        self.rejects("sampled physics interval")

    def test_status_activity_removed_consistently_rejected(self):
        path = self.directory / "frames.csv"
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            fields, rows = reader.fieldnames, list(reader)
        for row in rows:
            row["sim_statuses"] = "0"
        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        data = self.summary()
        data["sim_statuses"] = {key: 0 for key in ("min", "max", "p50", "p95", "p99")}
        self.write_summary(data)
        self.rejects("omitted actual status")


if __name__ == "__main__":
    unittest.main()
