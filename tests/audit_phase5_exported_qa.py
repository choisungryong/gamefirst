"""Read-only independent audit of external-PCK equipment QA artifacts."""
from pathlib import Path
import hashlib
import json
import struct
import sys

PROJECT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(directory: Path):
    build_path = PROJECT / "evidence/phase5/builds/phase5-candidate-20261029-01"
    mapping = json.loads((build_path / "source-manifest.json").read_text(encoding="utf-8-sig"))
    receipt = json.loads((build_path / "build.json").read_text(encoding="utf-8-sig"))
    catalog = json.loads((build_path / "source/game_data/catalog.json").read_text(encoding="utf-8-sig"))
    equipment = json.loads((build_path / "source/game_data/equipment.json").read_text(encoding="utf-8-sig"))
    oracle = json.loads((PROJECT / "evidence/phase5/verification/frozen-fingerprint-oracle-20261030.json").read_text())
    issues = []

    def require(ok, message):
        if not ok:
            issues.append(message)

    require(sha(Path(receipt["exe"])) == receipt["exe_sha256"], "Executable changed after external QA")
    for key in ("catalog", "equipment"):
        require(sha(build_path / ("source/game_data/" + key + ".json")) == mapping["game_data/" + key + ".json"], "Frozen QA definition hash mismatch")
    receipts = json.loads((directory / "qa-receipts.json").read_text(encoding="utf-8-sig"))
    require(len(receipts) == 2, "Two resolution receipts are required")
    output = []
    for dimensions in ((1440, 810), (1920, 1080)):
        case = directory / f"{dimensions[0]}x{dimensions[1]}"
        report = json.loads((case / "qa-report.json").read_text(encoding="utf-8-sig"))
        launch = json.loads((directory / f"{dimensions[0]}x{dimensions[1]}-launch.json").read_text(encoding="utf-8-sig"))
        actual = next(item for item in receipts if tuple(item["dimensions"]) == dimensions)
        require(actual["actual_exit"] == 0 and actual["stderr_bytes"] == 0 and actual["checks"] == 35, "External QA process did not exit cleanly with all checks")
        require(report["success"] is True and report["failures"] == [] and report["checks"] == 35, "External QA reported failure")
        require(report["metadata_sha256"] == mapping["game_data/build_info.json"] == launch["metadata_sha256"], "PCK metadata is not accepted metadata")
        require(report["metadata"]["source_hashes"] == {key: value for key, value in mapping.items() if key != "game_data/build_info.json"}, "PCK source map differs from export source map")
        require(report["external_script_sha256"] == launch["external_script_sha256"] == sha(PROJECT / "tests/phase5_exported_qa.gd"), "External QA script changed after execution")
        require(launch["exe_sha256"] == receipt["exe_sha256"], "QA launch executable differs")
        require(report["original_source_text_present"] is False and report["resource_root"] == "", "Expected exported script remap/PCK root observations differ")
        require(Path(report["executable"]).resolve() == Path(receipt["exe"]).resolve(), "Runtime executable differs")
        require(Path(report["working_directory"]).resolve() == Path(receipt["exe"]).parent.resolve(), "External QA fallback save root is not candidate directory")
        require(report["normal_user_save_before"] == report["normal_user_save_after"] == "absent", "QA touched normal user save")
        save_path = Path(report["isolated_save_path"])
        require(save_path.resolve().is_relative_to(Path(receipt["exe"]).parent.resolve() / "evidence/phase5"), "QA save escaped candidate phase5 directory")
        require(sha(save_path) == report["isolated_save_sha256"], "Saved bytes changed after QA")
        saved = json.loads(save_path.read_text(encoding="utf-8-sig"))
        state = report["final"]
        require(saved == state["equipment"], "Final equipment differs from saved snapshot")
        require(saved["equipped"] == {"focus": 1, "body": 2} and saved["catalog_sha256"] == oracle["equipment_content_fingerprint"], "Saved equipment/definition fingerprint differs")
        require(state["paused"] is True and state["modal"] is False, "Equipment did not close into previous ordinary pause")
        definitions = {item["id"]: item for item in equipment["items"]}
        affixes = {item["id"]: item for item in equipment["affixes"]}
        stats = {item["id"]: item for item in catalog["stats"]}
        values = {key: int(item.get("default_raw", 0)) for key, item in stats.items()}
        player = catalog["player"]
        values[player["health_stat_id"]] = int(player["max_health_raw"])
        values[player["mana_stat_id"]] = int(player["max_mana_raw"])
        flat, percent = {key: 0 for key in values}, {key: 0 for key in values}
        owned = {item["uid"]: item for item in saved["items"]}
        require(set(owned) == {1, 2, 3} and saved["next_uid"] == 4, "Saved owned instance identities differ")
        for slot, uid in saved["equipped"].items():
            item = owned[uid]
            definition = definitions[item["base_id"]]
            require(definition["slot"] == slot and definition["minimum_level"] <= 1 and definition["actor_tag"] == "caster", "Saved equipment fails base owner requirements")
            modifiers = list(definition["base_modifiers"])
            require(len(item["affixes"]) == 1, "Saved crafted item lacks one affix")
            roll = item["affixes"][0]
            affix = affixes[roll["id"]]
            spec = affix["modifier"]
            require(roll["id"] in definition["affix_ids"] and affix["required_tag"] in definition["tags"] and spec["minimum"] <= roll["value"] <= spec["maximum"] and (roll["value"] - spec["minimum"]) % spec["step"] == 0, "Saved affix roll invalid")
            modifiers.append({"stat_id": spec["stat_id"], "operation": spec["operation"], "value": roll["value"]})
            for modifier in modifiers:
                (flat if modifier["operation"] == "add" else percent)[modifier["stat_id"]] += int(modifier["value"])
        for key, spec in stats.items():
            values[key] = min(int(spec.get("maximum_raw", 2147483647)), max(int(spec.get("minimum_raw", 0)), (values[key] + flat[key]) * max(0, 10000 + percent[key]) // 10000))
        require(state["stats"] == values, "QA final stats differ from independent two-item oracle")
        require(state["life"] * 256 == state["life_max_raw"] == values[player["health_stat_id"]] and state["mana_raw"] == values[player["mana_stat_id"]], "Explicit R did not reset modified maxima")
        skill = next(item for item in catalog["skills"] if item["id"] == catalog["experiment"]["skill_id"])
        curve = skill["bonus_curve"]
        bonus = min(20, max(0, values[curve["stat_id"]]))
        power = 10000 + values["stat.spell_power"]
        minimum = (int(skill["damage"]["min_raw"]) + bonus * int(curve["min_per_bonus_raw"])) * power // 10000
        maximum = (int(skill["damage"]["max_raw"]) + bonus * int(curve["max_per_bonus_raw"])) * power // 10000
        require(state["skill"]["damage_min_raw"] == minimum and state["skill"]["damage_max_raw"] == maximum and state["skill"]["effective_level"] == bonus + 1 and "Lv.2" in state["hud"], "QA equipped skill/HUD differs from independent oracle")
        require(len(report["captures"]) == 5, "Expected five actual GPU captures per resolution")
        for capture in report["captures"]:
            path = Path(capture["path"])
            require(path.resolve().is_relative_to(case.resolve()) and sha(path) == capture["sha256"], "Capture bytes/path differ")
            blob = path.read_bytes()
            require(blob[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", blob[16:24]) == dimensions == tuple(capture["dimensions"]), "Capture is not actual requested framebuffer")
        output.append({"dimensions": list(dimensions), "checks": report["checks"], "captures": len(report["captures"]), "saved_sha256": report["isolated_save_sha256"], "final_life": state["life"], "final_mana_raw": state["mana_raw"], "damage_raw": [minimum, maximum]})
    return {"scope": "Read-only artifact consistency; external direct-signal QA is distinct from OS routing/performance", "success": not issues, "failures": issues, "cases": output}


if __name__ == "__main__":
    directory = Path(sys.argv[1])
    result = audit(directory)
    if len(sys.argv) > 2:
        target = Path(sys.argv[2])
        if target.exists():
            raise SystemExit("Preserve previous audit")
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["success"] else 1)
