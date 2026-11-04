"""Adversarial fixtures for independent benchmark-evidence auditing."""
import csv
import json
import struct
import tempfile
import unittest
from pathlib import Path

from audit_phase3_runs import audit_run, ranks


class EvidenceAuditTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)
        self.rows = [
            {
                "elapsed_seconds": number / 100,
                "frame_ms": 10,
                "tick": number,
                "sim_active": 300,
                "sim_alive": 300,
                "render_actors": 300,
                "actor_centers_in_frustum": 300,
                "skinned_rigs": 300,
            }
            for number in range(1, 101)
        ]
        self.data = {
            "sample_count": 100,
            "warmup_seconds": 0,
            "requested_sample_seconds": 1.01,
            "wall_elapsed_seconds": 1.02,
            "sample_first_elapsed": 0.01,
            "sample_last_elapsed": 1.0,
            "stutter_gt50": 0,
            "requested": 300,
            "mode": "rig",
            "capture_saved": True,
            "framebuffer_width": 1920,
            "framebuffer_height": 1080,
            "adapter": "synthetic fixture, not a measured GPU",
            "display_server": "Windows",
            "rendering_method": "gl_compatibility",
            "max_fps": 0,
            "vsync_mode": 0,
        }
        for key in self.rows[0]:
            if key != "elapsed_seconds":
                self.data[key] = ranks([row[key] for row in self.rows])
        self.write()

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, dimensions=(1920, 1080)):
        (self.directory / "summary.json").write_text(json.dumps(self.data), encoding="utf-8")
        with (self.directory / "frames.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(self.rows[0]))
            writer.writeheader()
            writer.writerows(self.rows)
        # Only the dimensions/header are needed by this metadata audit. This
        # synthetic fixture is never presented as an actual framebuffer image.
        (self.directory / "frame.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + struct.pack(">II", *dimensions))
        if hasattr(self, "physics"):
            with (self.directory / "physics.csv").open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(self.physics[0]))
                writer.writeheader()
                writer.writerows(self.physics)

    def restat(self):
        for key in self.rows[0]:
            if key != "elapsed_seconds":
                self.data[key] = ranks([row[key] for row in self.rows])
        if hasattr(self, "physics"):
            for key in self.physics[0]:
                if key not in ("elapsed_seconds", "tick"):
                    self.data[key] = ranks([row[key] for row in self.physics])

    def explicit_window(self):
        self.data.update({
            "requested_sample_seconds": 1.0,
            "wall_elapsed_seconds": 1.0,
            "sample_start_elapsed": 0.0,
            "measured_sample_seconds": 1.0,
            "capture_elapsed": -0.1,
            "sample_start_tick": 0,
            "sample_end_tick": 60,
            "physics_sample_count": 60,
            "time_scale": 1,
            "animation_probe_windows": [{"window_start_elapsed": 0.0, "window_end_elapsed": 1.0, "advanced_clock_count": 100, "bone_pose_changed": True}],
        })
        for index, row in enumerate(self.rows):
            tick = (index + 1) * 60 // 100
            previous_tick = index * 60 // 100
            row.update({
                "tick": tick,
                "physics_ticks_in_frame": tick - previous_tick,
                "sim_frame_ms": (tick - previous_tick) * 0.1,
                "animation_clock_progress": 1,
                "animation_playing": 299,
            })
        self.physics = [{"elapsed_seconds": tick / 60, "tick": tick, "sim_tick_ms": 0.1} for tick in range(1, 61)]
        self.restat()
        self.write()

    def test_explicit_short_diagnostic(self):
        self.assertTrue(audit_run(self.directory, diagnostic=True)["integrity_pass"])

    def test_short_run_cannot_be_final(self):
        result = audit_run(self.directory)
        self.assertFalse(result["integrity_pass"])
        self.assertIn("Final benchmark sample is shorter than 60 seconds", result["failures"])

    def test_false_percentile_is_rejected(self):
        self.data["frame_ms"]["p95"] = 0.1
        self.write()
        self.assertFalse(audit_run(self.directory, diagnostic=True)["integrity_pass"])

    def test_dead_population_is_rejected(self):
        self.rows[50]["sim_alive"] = 299
        self.write()
        self.assertFalse(audit_run(self.directory, diagnostic=True)["integrity_pass"])

    def test_duplicate_timestamps_are_rejected(self):
        self.rows[50]["elapsed_seconds"] = self.rows[49]["elapsed_seconds"]
        self.write()
        self.assertFalse(audit_run(self.directory, diagnostic=True)["integrity_pass"])

    def test_actual_png_dimension_overrides_report(self):
        self.write(dimensions=(1440, 810))
        self.assertFalse(audit_run(self.directory, diagnostic=True)["integrity_pass"])

    def test_headless_is_not_gpu_evidence(self):
        self.data["display_server"] = "headless"
        self.write()
        self.assertFalse(audit_run(self.directory, diagnostic=True)["integrity_pass"])

    def test_timing_goal_is_separate_from_integrity(self):
        result = audit_run(self.directory, diagnostic=True, goal_ms=1)
        self.assertTrue(result["integrity_pass"])
        self.assertFalse(result["p95_goal_pass"])

    def test_reported_rows_are_required(self):
        self.data["sample_count"] = 200
        self.write()
        self.assertFalse(audit_run(self.directory, diagnostic=True)["integrity_pass"])

    def test_frozen_sim_is_rejected(self):
        for row in self.rows:
            row["tick"] = 1
        self.data["tick"] = ranks([row["tick"] for row in self.rows])
        self.write()
        self.assertFalse(audit_run(self.directory, diagnostic=True)["integrity_pass"])

    def test_missing_columns_are_rejected(self):
        (self.directory / "frames.csv").write_text("frame_ms\n10\n", encoding="utf-8")
        self.assertFalse(audit_run(self.directory, diagnostic=True)["integrity_pass"])

    def test_invalid_summary_shape_is_rejected(self):
        (self.directory / "summary.json").write_text("[]", encoding="utf-8")
        self.assertFalse(audit_run(self.directory, diagnostic=True)["integrity_pass"])

    def test_explicit_window_and_tick_aggregation(self):
        self.explicit_window()
        self.assertTrue(audit_run(self.directory, diagnostic=True)["integrity_pass"])

    def test_frozen_animation_window_is_rejected(self):
        self.explicit_window()
        for row in self.rows:
            row["animation_clock_progress"] = 0
        self.restat()
        self.write()
        result = audit_run(self.directory, diagnostic=True)
        self.assertFalse(result["integrity_pass"])
        self.assertIn("Actual animation clocks froze in sample second 0", result["failures"])

    def test_report_generation_cannot_inflate_sample_duration(self):
        self.explicit_window()
        self.data["measured_sample_seconds"] = 1.4
        self.write()
        self.assertFalse(audit_run(self.directory, diagnostic=True)["integrity_pass"])

    def test_duplicated_physics_tick_is_rejected(self):
        self.explicit_window()
        self.physics[10]["tick"] = self.physics[9]["tick"]
        self.write()
        self.assertFalse(audit_run(self.directory, diagnostic=True)["integrity_pass"])

    def test_stale_frame_cpu_aggregation_is_rejected(self):
        self.explicit_window()
        for row in self.rows:
            row["sim_frame_ms"] = 0
        self.restat()
        self.write()
        self.assertFalse(audit_run(self.directory, diagnostic=True)["integrity_pass"])

    def test_bone_pose_freeze_is_rejected(self):
        self.explicit_window()
        self.data["animation_probe_windows"][0]["bone_pose_changed"] = False
        self.write()
        self.assertFalse(audit_run(self.directory, diagnostic=True)["integrity_pass"])

    def test_probe_clock_count_must_match_raw_frames(self):
        self.explicit_window()
        self.data["animation_probe_windows"][0]["advanced_clock_count"] = 500
        self.write()
        self.assertFalse(audit_run(self.directory, diagnostic=True)["integrity_pass"])

    def skill_window(self):
        self.explicit_window()
        self.data.update({
            "workload": "skill",
            "mode": "fx",
            "fixture_bolts": 0,
            "skill_budget": {"cycle_ticks": 33, "projectile_life_ticks": 132, "theoretical_max_simultaneous_bolts": 4, "mana_cost_raw": 640},
            "sample_event_counts": {"cast_start": 2, "release": 2, "hit": 2},
            "cast_proxy_count": 2,
            "configuration": {"mana_refilled_every_tick": True},
        })
        for row in self.rows:
            row["bolts"] = 0
            row["fx_particles"] = 6
        self.restat()
        self.write()

    def test_actual_skill_events_and_zero_inflight_are_valid(self):
        self.skill_window()
        self.assertTrue(audit_run(self.directory, diagnostic=True)["integrity_pass"])

    def test_injected_four_bolts_are_not_actual_skill(self):
        self.skill_window()
        self.data["fixture_bolts"] = 4
        self.write()
        self.assertFalse(audit_run(self.directory, diagnostic=True)["integrity_pass"])

    def test_wrong_skill_budget_is_rejected(self):
        self.skill_window()
        self.data["skill_budget"]["cycle_ticks"] = 10
        self.write()
        self.assertFalse(audit_run(self.directory, diagnostic=True)["integrity_pass"])

    def test_missing_real_fx_is_rejected(self):
        self.skill_window()
        for row in self.rows:
            row["fx_particles"] = 0
        self.restat()
        self.write()
        self.assertFalse(audit_run(self.directory, diagnostic=True)["integrity_pass"])

    def final_window(self):
        """Synthetic complete protocol fixture, never measured GPU evidence."""
        self.explicit_window()
        template = self.rows[0].copy()
        self.rows = []
        for index in range(6000):
            tick = 600 + (index + 1) * 60 // 100
            previous_tick = 600 + index * 60 // 100
            row = template.copy()
            row.update({
                "elapsed_seconds": 10 + (index + 1) / 100,
                "tick": tick,
                "physics_ticks_in_frame": tick - previous_tick,
                "sim_frame_ms": (tick - previous_tick) * 0.1,
            })
            self.rows.append(row)
        self.physics = [{"elapsed_seconds": 10 + tick / 60, "tick": 600 + tick, "sim_tick_ms": 0.1} for tick in range(1, 3601)]
        project = Path(__file__).resolve().parents[1]
        metadata = json.loads((project / "game_data" / "build_info.json").read_text(encoding="utf-8-sig"))
        manifest = json.loads((project / "evidence" / "phase3" / "source-manifest.json").read_text(encoding="utf-8-sig"))
        metadata_hash = next(item["sha256"] for item in manifest if item["path"].replace("\\", "/") == "game_data/build_info.json")
        build = json.loads((project / "evidence" / "phase3" / "final-build.json").read_text(encoding="utf-8-sig"))
        self.data.update({
            "warmup_seconds": 10, "requested_sample_seconds": 60,
            "wall_elapsed_seconds": 70, "sample_start_elapsed": 10,
            "measured_sample_seconds": 60, "sample_first_elapsed": 10.01,
            "sample_last_elapsed": 70, "capture_elapsed": 9,
            "sample_start_tick": 600, "sample_end_tick": 4200,
            "physics_sample_count": 3600, "sample_count": 6000,
            "source_hashes_basis": "embedded synthetic pre-export map fixture",
            "source_hashes": metadata["source_hashes"],
            "embedded_source_manifest_sha256": metadata_hash,
            "animation_probe_windows": [
                {"window_start_elapsed": 10 + index, "window_end_elapsed": 11 + index, "advanced_clock_count": 100, "bone_pose_changed": True}
                for index in range(60)
            ],
        })
        self.restat()
        self.write()
        self.launch = {"exe_sha256": build["exe_sha256"], "embedded_preexport_manifest_sha256": metadata_hash}
        (self.directory / "launch.json").write_text(json.dumps(self.launch), encoding="utf-8")

    def test_complete_final_protocol_fixture(self):
        self.final_window()
        self.assertTrue(audit_run(self.directory)["integrity_pass"])

    def test_final_cannot_omit_explicit_measurement_window(self):
        self.final_window()
        self.data.pop("sample_start_elapsed")
        self.write()
        result = audit_run(self.directory)
        self.assertIn("Final evidence lacks the explicit fixed measurement window", result["failures"])

    def test_final_wrong_executable_hash_is_rejected(self):
        self.final_window()
        self.launch["exe_sha256"] = "0" * 64
        (self.directory / "launch.json").write_text(json.dumps(self.launch), encoding="utf-8")
        result = audit_run(self.directory)
        self.assertIn("External launch executable hash differs from the accepted final build", result["failures"])

    def test_final_requires_external_launch_provenance(self):
        self.final_window()
        (self.directory / "launch.json").unlink()
        result = audit_run(self.directory)
        self.assertIn("Final release evidence lacks its external launch record", result["failures"])

    def test_lod_flag_cannot_erase_full_rig_condition(self):
        self.explicit_window()
        self.data["lod_enabled"] = True
        for row in self.rows:
            row["skinned_rigs"] = 299
        self.restat()
        self.write()
        result = audit_run(self.directory, diagnostic=True)
        self.assertIn("Full-rig condition did not retain all requested rigs", result["failures"])


if __name__ == "__main__":
    unittest.main()
