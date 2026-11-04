"""Independently recompute phase5 equipped benchmark evidence from raw CSV/PNG.

Does not launch the renderer. Integrity and the 300-actor timing goal are separate.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import struct
import hashlib
from collections import Counter, defaultdict
from pathlib import Path
from copy import deepcopy


def exact_integer(value, minimum, maximum):
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value) and value == int(value) and minimum <= value <= maximum


def damage_reachable(damage: int, contract: dict) -> bool:
    """Invert each integer floor interval; detects in-range impossible rolls."""
    resistance_factor = 10000 - contract["resistance_bps"]
    if resistance_factor == 0:
        return damage == 0
    after_flat_lo = (damage * 10000 + resistance_factor - 1) // resistance_factor
    after_flat_hi = ((damage + 1) * 10000 - 1) // resistance_factor
    after_power_lo = 0 if after_flat_lo == 0 else after_flat_lo + contract["flat_raw"]
    after_power_hi = after_flat_hi + contract["flat_raw"]
    power_factor = 10000 + contract["power_bps"]
    if power_factor == 0:
        return after_power_lo <= 0 <= after_power_hi
    base_lo = (after_power_lo * 10000 + power_factor - 1) // power_factor
    base_hi = ((after_power_hi + 1) * 10000 - 1) // power_factor
    return max(base_lo, contract["base_min"]) <= min(base_hi, contract["base_max"])


def frozen_document(manifest_path: Path, relative: str) -> dict:
    mapping = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    blob = (manifest_path.parent / "source" / relative).read_bytes()
    if hashlib.sha256(blob).hexdigest() != mapping[relative].lower():
        raise ValueError("Frozen definition bytes differ: " + relative)
    return json.loads(blob.decode("utf-8-sig"))


def equipped_contract(catalog: dict, equipment: dict, data: dict, oracle: dict) -> tuple[dict, dict]:
    """Integer oracle from frozen definitions and independently checked rolls.

    Does not import GDScript or trust reported derived stats/skill quantities.
    RNG algorithm equivalence is a separate functional test; here its saved
    representation and unchanged initial inventory identity are checked.
    """
    fixture = data["equipment_fixture"]
    if fixture != data["configuration"]["equipment_fixture"] or fixture["enabled"] is not True:
        raise ValueError("Equipped fixture/configuration mismatch or disabled fixture")
    if fixture["context"] != {"actor_tag": "caster", "level": 2}:
        raise ValueError("Equipped synthetic owner context differs")
    inventory = fixture["inventory"]
    if not exact_integer(inventory["schema_version"], 1, 1) or inventory["catalog_id"] != equipment["catalog_id"] or not exact_integer(inventory["definition_version"], equipment["definition_version"], equipment["definition_version"]):
        raise ValueError("Inventory definition identity mismatch")
    fingerprint = inventory["catalog_sha256"]
    if not isinstance(fingerprint, str) or len(fingerprint) != 64 or any(c not in "0123456789abcdef" for c in fingerprint):
        raise ValueError("Invalid saved definition fingerprint representation")
    if fingerprint != oracle["equipment_content_fingerprint"]:
        raise ValueError("Saved definition fingerprint differs from independent frozen JSON oracle")
    state = inventory["rng_state"]
    if not isinstance(state, str) or str(int(state)) != state or not -(1 << 63) <= int(state) < (1 << 63):
        raise ValueError("Saved item RNG is not canonical signed64 decimal")
    if not exact_integer(inventory["next_uid"], 4, 4) or len(inventory["items"]) != 3 or inventory["equipped"] != {"focus": 1, "body": 2, "charm": 3} or any(not exact_integer(value, 1, 3) for value in inventory["equipped"].values()):
        raise ValueError("Three initial owned/equipped items are not present")
    bases = {item["id"]: item for item in equipment["items"]}
    affixes = {item["id"]: item for item in equipment["affixes"]}
    stats = {item["id"]: item for item in catalog["stats"]}
    values = {key: int(value.get("default_raw", 0)) for key, value in stats.items()}
    player = catalog["player"]
    values[player["health_stat_id"]] = int(player["max_health_raw"])
    values[player["mana_stat_id"]] = int(player["max_mana_raw"])
    adds, percents = defaultdict(int), defaultdict(int)
    for index, instance in enumerate(inventory["items"], 1):
        if not exact_integer(instance["uid"], index, index) or instance["quality"] != "crafted" or len(instance["affixes"]) != 1:
            raise ValueError("Invalid initial item identity/quality/affix count")
        base = bases[instance["base_id"]]
        if base["id"] != equipment["items"][index - 1]["id"] or inventory["equipped"][base["slot"]] != index:
            raise ValueError("Equipment order or slot differs from initial definitions")
        if base["actor_tag"] != "caster" or base["minimum_level"] > 2:
            raise ValueError("Equipped item requirements are not met")
        modifiers = deepcopy(base["base_modifiers"])
        roll = instance["affixes"][0]
        if roll["id"] not in base["affix_ids"]:
            raise ValueError("Ineligible equipped affix")
        definition = affixes[roll["id"]]
        modifier = definition["modifier"]
        number = roll["value"]
        if definition["required_tag"] not in base["tags"] or isinstance(number, bool) or not isinstance(number, (int, float)) or not math.isfinite(number) or int(number) != number or not modifier["minimum"] <= number <= modifier["maximum"] or (int(number) - int(modifier["minimum"])) % int(modifier["step"]):
            raise ValueError("Equipped affix roll/tag/step outside frozen definition")
        modifiers.append({"stat_id": modifier["stat_id"], "operation": modifier["operation"], "value": int(number)})
        for entry in modifiers:
            if entry["stat_id"] not in stats or entry["operation"] not in ("add", "percent_bps"):
                raise ValueError("Unsupported equipped modifier")
            (adds if entry["operation"] == "add" else percents)[entry["stat_id"]] += int(entry["value"])
    # The harness equips first, then uses its public external modifier to make
    # maximum/current health 1e9 raw. Other equipment stats remain effective.
    health = player["health_stat_id"]
    before_fixture = (values[health] + adds[health]) * max(0, 10000 + percents[health]) // 10000
    adds[health] += 1000000000 - before_fixture
    for key, definition in stats.items():
        raw = (values[key] + adds[key]) * max(0, 10000 + percents[key]) // 10000
        values[key] = min(int(definition.get("maximum_raw", 2147483647)), max(int(definition.get("minimum_raw", 0)), raw))
    if fixture["stats"] != values or any(not exact_integer(value, -2147483647, 2147483647) for value in fixture["stats"].values()) or values[health] != 1000000000:
        raise ValueError("Reported equipped stats differ from independent modifier oracle")
    actual = {item["id"]: item for item in fixture["skills"]}
    definitions = deepcopy({item["id"]: item for item in catalog["skills"]})
    if set(actual) != set(definitions) or len(fixture["skills"]) != len(definitions):
        raise ValueError("Reported equipped skill set differs from frozen skills")
    speed = min(30000, max(-7500, values["stat.cast_speed"]))
    power = min(100000, max(-10000, values["stat.spell_power"]))
    cost_bps = min(100000, max(-9000, values["stat.mana_cost"]))
    for key, definition in definitions.items():
        curve = definition.get("bonus_curve", {})
        bonus = min(20, max(0, values[curve["stat_id"]])) if curve else 0
        lo = min(2147483647, int(definition["damage"]["min_raw"]) + bonus * int(curve.get("min_per_bonus_raw", 0)))
        hi = min(2147483647, int(definition["damage"]["max_raw"]) + bonus * int(curve.get("max_per_bonus_raw", 0)))
        enemy = next(item for item in catalog["enemies"] if item["id"] == catalog["experiment"]["enemy_id"])
        defenses = enemy.get("defenses", {})
        resistance_id = "stat.resist." + definition["damage"]["element"]
        flat = int(defenses.get("stat.flat_reduction", stats["stat.flat_reduction"].get("default_raw", 0)))
        resistance = int(defenses.get(resistance_id, stats[resistance_id].get("default_raw", 0)))
        definition["_audit_damage_contract"] = {"base_min": lo, "base_max": hi, "power_bps": power, "flat_raw": min(2147483647, max(0, flat)), "resistance_bps": min(10000, max(-10000, resistance))}
        lo = lo * (10000 + power) // 10000
        hi = hi * (10000 + power) // 10000
        startup = (int(definition["startup_ticks"]) * 10000 + 9999 + speed) // (10000 + speed)
        cycle = max(startup + 1, (int(definition["cycle_ticks"]) * 10000 + 9999 + speed) // (10000 + speed))
        cost = max(1, int(definition["cost"]["raw"]) * (10000 + cost_bps) // 10000)
        display = actual[key]
        expected = {"damage_min_raw": lo, "damage_max_raw": hi, "startup_ticks": startup, "cycle_ticks": cycle, "cost_raw": cost, "bonus_level": bonus, "effective_level": bonus + 1}
        if any(not exact_integer(display.get(field), value, value) for field, value in expected.items()):
            raise ValueError("Reported equipped skill differs from independent integer oracle: " + key)
        definition["damage"]["min_raw"], definition["damage"]["max_raw"] = lo, hi
        definition["startup_ticks"], definition["cycle_ticks"] = startup, cycle
        definition["cost"]["raw"] = cost
    return definitions, values


def ranks(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    return {
        "min": ordered[0],
        "max": ordered[-1],
        **{f"p{p}": ordered[max(0, math.ceil(len(ordered) * p / 100) - 1)] for p in (50, 95, 99)},
    }


def frozen_catalog(project: Path, manifest_path: Path | None) -> tuple[dict, str]:
    path = manifest_path or project / "evidence/phase5/builds/phase5-candidate-20261029-01/source-manifest.json"
    mapping = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(mapping, dict):
        mapping = {item["path"].replace("\\", "/"): item["sha256"] for item in mapping}
    catalog_bytes = (path.parent / "source/game_data/catalog.json").read_bytes()
    expected = mapping["game_data/catalog.json"].lower()
    if hashlib.sha256(catalog_bytes).hexdigest() != expected:
        raise ValueError("Frozen catalog bytes differ from explicit export manifest")
    return json.loads(catalog_bytes.decode("utf-8-sig")), expected


def audit_run(directory: Path, *, diagnostic: bool = False, goal_ms: float = 16.67, source_manifest_path: Path | None = None, build_record_path: Path | None = None) -> dict:
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
    require(requested == 300, "Phase5 equipment gate requires exactly 300 enemies")
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
            catalog, catalog_hash = frozen_catalog(project, source_manifest_path)
            require(data.get("catalog_sha256", "").lower() == catalog_hash, "Runtime catalog differs from frozen export catalog")
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
        require(data.get("workload") in ("projectile_stress", "multi_skill"), "Final FX evidence does not declare its workload")

    if data.get("workload") == "multi_skill":
        try:
            project = Path(__file__).resolve().parents[1]
            catalog, catalog_hash = frozen_catalog(project, source_manifest_path)
            require(data.get("catalog_sha256", "").lower() == catalog_hash, "Runtime catalog differs from frozen export catalog")
            immutable_manifest = source_manifest_path or project / "evidence/phase5/builds/phase5-candidate-20261029-01/source-manifest.json"
            equipment = frozen_document(immutable_manifest, "game_data/equipment.json")
            oracle = json.loads((project / "evidence/phase5/verification/frozen-fingerprint-oracle-20261030.json").read_text())
            source_map = json.loads(immutable_manifest.read_text(encoding="utf-8-sig"))
            for key in ("catalog", "equipment"):
                require(oracle[key + "_sha256"] == source_map["game_data/" + key + ".json"].lower(), "Fingerprint oracle input hashes differ from frozen export")
            require(oracle["oracle_script_sha256"] == hashlib.sha256((project / "tests/phase5_fingerprint_oracle.gd").read_bytes()).hexdigest(), "Fingerprint oracle script changed after its execution")
            definitions, equipped_stats = equipped_contract(catalog, equipment, data, oracle)
            ids = list(definitions)
            default_skill = catalog["experiment"]["skill_id"]
            require(data.get("skill_round_robin_ids") == ids and len(ids) == 3, "Multi-skill rotation differs from three catalog skills")
            require(data.get("fixture_bolts") == 0 and data.get("configuration", {}).get("fixture_bolts") == 0, "Multi-skill run injects uncommitted fixture projectiles")
            require(data.get("configuration", {}).get("mana_refilled_every_tick") is True, "Sustained multi-skill refill is undeclared")
            require(data.get("combat_errors") == [], "Common combat path reported context failures")
            events = [json.loads(line) for line in (directory / "skill-events.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
            require(bool(events), "Multi-skill raw event log is empty")
            total_counts = Counter()
            skill_counts = {skill_id: Counter() for skill_id in ids}
            casts = []
            release_by_shot = {}
            hits_by_shot = defaultdict(list)
            cast_releases = set()
            releases = []
            hurt_life_raw = []
            start_tick, end_tick = int(data["sample_start_tick"]), int(data["sample_end_tick"])
            last_tick, last_time = start_tick, sample_start
            for entry in events:
                event = entry["event"]
                stamp, tick = float(entry["elapsed_seconds"]), int(event["tick"])
                require(math.isfinite(stamp) and stamp >= last_time and sample_start <= stamp <= sample_end + boundary_tolerance, "Raw skill event time outside monotonic measurement interval")
                require(last_tick <= tick <= end_tick and tick > start_tick, "Raw skill event tick outside contiguous sampled physics interval")
                require(math.isclose(float(event["seconds"]), tick / 60, abs_tol=1e-10), "Event logical clock differs from 60Hz tick")
                last_tick, last_time = tick, stamp
                kind = event["kind"]
                skill_id = event.get("skill_id", default_skill)
                total_counts[kind] += 1
                if kind in ("cast_start", "release", "hit", "skill_effect", "status_applied"):
                    require(skill_id in definitions, "Raw event uses unknown skill")
                    if skill_id not in definitions:
                        continue
                    skill_counts[skill_id][kind] += 1
                if kind == "cast_start":
                    casts.append((tick, skill_id))
                    cast_releases.add((tick + definitions[skill_id]["startup_ticks"], skill_id))
                    require(event["release_tick"] == tick + definitions[skill_id]["startup_ticks"], "Committed startup differs from actual catalog")
                    require(event["mana_raw"] == equipped_stats[catalog["player"]["mana_stat_id"]] - definitions[skill_id]["cost"]["raw"], "Equipped cast cost differs from full-refill mana oracle")
                elif kind == "release":
                    shot = int(event["shot"])
                    require(shot not in release_by_shot, "Duplicate release for one shot")
                    release_by_shot[shot] = (tick, skill_id)
                    releases.append((shot, tick, skill_id))
                elif kind == "hit":
                    shot = int(event["shot"])
                    hits_by_shot[shot].append(event)
                    damage = int(event["damage_raw"])
                    damage_def = definitions[skill_id]["damage"]
                    require(damage >= 0 and damage_reachable(damage, definitions[skill_id]["_audit_damage_contract"]), "Equipped benchmark damage outside selected skill reachable raw rolls")
                    if shot in release_by_shot:
                        require(release_by_shot[shot][1] == skill_id, "Hit changed the released skill identity")
                elif kind == "skill_effect":
                    target_handles = [tuple(sorted(item.items())) for item in event["targets"]]
                    require(len(target_handles) == len(set(target_handles)) <= definitions[skill_id]["effect"]["max_targets"], "Instant skill event duplicates/exceeds target handles")
                    require(event["effect_kind"] == definitions[skill_id]["kind"], "Effect handler kind differs from selected definition")
                elif kind == "status_applied":
                    definition = definitions[skill_id]["effect"]["status"]
                    require(event["status"] == "chill" and event["slow_bps"] == definition["slow_bps"] and event["until_tick"] == tick + definition["duration_ticks"], "Raw chill strength/expiry differs from declared skill")
                elif kind == "player_hurt":
                    life_raw = float(event["life"]) * 256
                    require(math.isfinite(life_raw) and life_raw == int(life_raw) and life_raw > 0, "Player hurt HP is not exact positive raw health")
                    hurt_life_raw.append(int(life_raw))
            require(dict(total_counts) == data.get("sample_event_counts"), "Raw skill event log differs from total summary counts")
            require({key: dict(value) for key, value in skill_counts.items()} == data.get("sample_skill_event_counts"), "Raw per-skill counts differ from summary")
            for (prior_tick, prior_id), (tick, skill_id) in zip(casts, casts[1:]):
                require(skill_id == ids[(ids.index(prior_id) + 1) % len(ids)], "Accepted casts do not rotate through all three skills")
                require(tick - prior_tick == definitions[prior_id]["cycle_ticks"], "Accepted multi-skill cast interval differs from committed prior skill")
            for index, (shot, tick, skill_id) in enumerate(releases):
                if index:
                    require(shot == releases[index - 1][0] + 1, "Released shot IDs are not contiguous")
                # A startup committed just before the sample may release inside
                # it. Permit at most the first sampled release on this boundary.
                boundary_pending = index == 0 and tick - definitions[skill_id]["startup_ticks"] <= start_tick
                require((tick, skill_id) in cast_releases or boundary_pending, "Release lacks its committed sampled cast or first pending boundary")
            for tick, skill_id in casts:
                scheduled = tick + definitions[skill_id]["startup_ticks"]
                if scheduled <= end_tick:
                    require(any(release_tick == scheduled and release_skill == skill_id for _, release_tick, release_skill in releases), "Sampled cast did not release at its committed tick")
            for skill_id, counts in skill_counts.items():
                definition = definitions[skill_id]
                require(all(counts[kind] > 0 for kind in ("cast_start", "release", "hit")), f"Skill lacks real cast/release/hit: {skill_id}")
                if definition.get("kind", "projectile") != "projectile":
                    require(counts["skill_effect"] > 0, f"Instant skill lacks output event: {skill_id}")
                if "status" in definition.get("effect", {}):
                    require(counts["status_applied"] > 0, f"Cold skill lacks actual status application: {skill_id}")
            for shot, shot_hits in hits_by_shot.items():
                skill_id = shot_hits[0].get("skill_id", default_skill)
                # This dense benchmark resolves bolts immediately. We require
                # every sampled hit to join an observed release. A future flight
                # benchmark crossing a pre-sample release needs explicit warmup
                # provenance; absence is not silently accepted as a valid shot.
                require(shot in release_by_shot, f"Hit references unobserved release shot {shot}")
                if shot in release_by_shot:
                    released_tick, released_skill = release_by_shot[shot]
                    for event in shot_hits:
                        require(event.get("skill_id", default_skill) == released_skill, "Hit identity differs from observed release")
                        if definitions[skill_id].get("kind", "projectile") == "projectile":
                            projectile = next(item for item in catalog["projectiles"] if item["id"] == definitions[skill_id]["projectile_id"])
                            lifetime = round(projectile["lifetime_seconds"] * 60)
                            require(0 <= event["tick"] - released_tick <= lifetime, "Projectile hit outside observed release lifetime")
                        else:
                            require(event["tick"] == released_tick, "Instant skill hit outside its release tick")
                handles = [tuple(sorted(item["entity"].items())) for item in shot_hits]
                limit = definitions[skill_id].get("effect", {}).get("max_targets", 1)
                require(len(handles) == len(set(handles)) <= limit, f"Shot {shot} hit duplicate/excess targets")
            require(data.get("cast_proxy_count") == total_counts["cast_start"], "Actual proxy cast count differs from raw accepted casts")
            enemy = next(item for item in catalog["enemies"] if item["id"] == catalog["experiment"]["enemy_id"])
            flat = min(2147483647, max(0, equipped_stats["stat.flat_reduction"]))
            resistance = min(10000, max(-10000, equipped_stats["stat.resist.physical"]))
            incoming = max(0, int(enemy["attack"]["damage_raw"]) - flat) * (10000 - resistance) // 10000
            require(len(hurt_life_raw) > 1 and all(before - after == incoming for before, after in zip(hurt_life_raw, hurt_life_raw[1:])), "Equipped physical resistance differs from successive actual player-hurt events")
            require(max(row["fx_particles"] for row in rows) > 0 and max(row["skill_fx_active"] for row in rows) > 0 and max(row["skill_fx_status"] for row in rows) > 0 and max(row["sim_statuses"] for row in rows) > 0, "Multi-skill benchmark omitted actual status/area/chain/particle activity")
            require(data["skill_fx_pool"]["cap"] == 64 and 0 < data["skill_fx_pool"]["created"] <= 64, "New skill visual pool cap exceeded or not exercised")
        except (OSError, ValueError, TypeError, KeyError, IndexError) as error:
            require(False, f"Cannot independently verify multi-skill workload: {error}")

    for key, limit in (("history", 4096), ("actor_pool", 512), ("projectile_pool", 512), ("particle_pool", 256), ("fx_particles", 256), ("skill_fx_active", 64), ("skill_fx_status", 64), ("skill_fx_created", 64)):
        if key in rows[0]:
            require(max(row[key] for row in rows) <= limit, f"Game state exceeded its declared cap: {key}")

    if data.get("source_hashes_basis", "").startswith("embedded"):
        try:
            project = Path(__file__).resolve().parents[1]
            source_path = source_manifest_path or project / "evidence/phase5/builds/phase5-candidate-20261029-01/source-manifest.json"
            source_manifest = json.loads(source_path.read_text(encoding="utf-8-sig"))
            if isinstance(source_manifest, dict):
                expected_sources = {key.replace("\\", "/"): value.lower() for key, value in source_manifest.items()}
            else:
                expected_sources = {entry["path"].replace("\\", "/"): entry["sha256"].lower() for entry in source_manifest}
            metadata_hash = expected_sources.pop("game_data/build_info.json")
            actual_sources = {key.replace("\\", "/"): value.lower() for key, value in data["source_hashes"].items()}
            require(actual_sources == expected_sources, "Embedded pre-export source map differs from the frozen phase5 source manifest")
            require(data.get("embedded_source_manifest_sha256", "").lower() == metadata_hash, "Embedded metadata hash differs from the accepted source manifest")
            if (directory / "launch.json").is_file():
                launch = json.loads((directory / "launch.json").read_text(encoding="utf-8-sig"))
                if not diagnostic or "embedded_preexport_manifest_sha256" in launch:
                    require(launch.get("embedded_preexport_manifest_sha256", "").lower() == metadata_hash, "External launch metadata differs from runtime metadata")
                build_path = build_record_path or source_path.parent / "build.json"
                accepted_build = json.loads(build_path.read_text(encoding="utf-8-sig"))
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
    formal_eligible = warmup >= 10 and duration >= 60 and requested == 300 and mode == "fx"
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
        "formal_window_eligible": formal_eligible,
        "formal_goal_pass": not failures and formal_eligible and percentiles["p95"] <= goal_ms,
        "goal_scope": "timing threshold only; does not establish art, game balance or original-game equivalence",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directories", nargs="+", type=Path)
    parser.add_argument("--diagnostic", action="store_true", help="Allow explicitly labelled short diagnostic runs")
    parser.add_argument("--require-goal", action="store_true", help="Also fail if the p95 timing threshold is missed")
    parser.add_argument("--goal-ms", type=float, default=16.67)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--source-manifest", type=Path, help="Explicit immutable export source manifest")
    parser.add_argument("--build-record", type=Path, help="Matching immutable export build record")
    options = parser.parse_args()
    if not math.isfinite(options.goal_ms) or options.goal_ms < 0:
        parser.error("--goal-ms must be finite and nonnegative")
    results = [audit_run(path, diagnostic=options.diagnostic, goal_ms=options.goal_ms, source_manifest_path=options.source_manifest, build_record_path=options.build_record) for path in options.directories]
    success = all(result["integrity_pass"] and (not options.require_goal or result.get("formal_goal_pass", False)) for result in results)
    output = {"scope": "independent raw evidence audit; integrity and timing goals are separate", "success": success, "runs": results}
    if options.output:
        options.output.parent.mkdir(parents=True, exist_ok=True)
        options.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
