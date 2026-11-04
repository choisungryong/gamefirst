"""Audit final ordinary-scene QA reports, actual process exits and PNG sizes."""
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
directory = Path(sys.argv[1])
build_path = Path(sys.argv[2])
output = Path(sys.argv[3])
build = json.loads(build_path.read_text(encoding="utf-8-sig"))
manifest_path = Path(build["source_manifest"])
manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
catalog_bytes = (manifest_path.parent / "source/game_data/catalog.json").read_bytes()
failures = []


def require(ok, message):
    if not ok:
        failures.append(message)


require(hashlib.sha256(catalog_bytes).hexdigest() == manifest["game_data/catalog.json"], "Frozen QA catalog hash")
catalog = json.loads(catalog_bytes.decode("utf-8-sig"))
definitions = {item["id"]: item for item in catalog["skills"]}
receipts = json.loads((directory / "qa-receipts.json").read_text(encoding="utf-8-sig"))
require(len(receipts) == 6, "Six required ordinary-scene QA cases")
result = []
for receipt in receipts:
    name = receipt["name"]
    case = directory / name
    launch = json.loads((case / "launch.json").read_text(encoding="utf-8-sig"))
    data = json.loads((case / "scene-run.json").read_text(encoding="utf-8-sig"))
    skill_id = launch["requested_skill"]
    skill = definitions[skill_id]
    require(receipt["actual_exit"] == 0 and receipt["stderr_bytes"] == 0, name + " actual process exit/stderr")
    require(receipt["exe_sha256"] == launch["exe_sha256"] == build["exe_sha256"], name + " same frozen executable")
    require(launch["embedded_preexport_manifest_sha256"] == manifest["game_data/build_info.json"], name + " same embedded source metadata")
    require(data["requested_enemies"] == launch["requested_enemies"] == data["entities"] == data["actor_count"], name + " population/actors reflect requested count")
    require(data["capture_saved"] and data["tick"] >= 175, name + " ordinary scene actually ran and captured")
    prefix = (case / "frame.png").read_bytes()[:24]
    require(prefix[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", prefix[16:24]) == (1920, 1080), name + " actual PNG1920x1080")
    require((data["framebuffer_width"], data["framebuffer_height"]) == (1920, 1080), name + " actual framebuffer matches report")
    trace = data["events"]
    require(all(a["tick"] <= b["tick"] for a, b in zip(trace, trace[1:])), name + " event tick order")
    casts = [event for event in trace if event["kind"] == "cast_start"]
    releases = [event for event in trace if event["kind"] == "release"]
    hits = [event for event in trace if event["kind"] == "hit"]
    effects = [event for event in trace if event["kind"] == "skill_effect"]
    require(data["shots"] == len(releases) and data["hits"] == len(hits), name + " runtime counters equal real release/hit trace")
    require(data["mana_raw"] == catalog["player"]["max_mana_raw"] - len(casts) * skill["cost"]["raw"], name + " actual selected-skill cost charged exactly once per accepted request")
    require(all(event.get("skill_id", catalog["experiment"]["skill_id"]) == skill_id for event in casts + releases + hits), name + " accepted/released/hit skill identity")
    if launch["requested_enemies"] == 0:
        require(not casts and not releases and not hits and data["alive"] == 0, name + " zero-target QA does not cast")
    else:
        require(casts and releases and hits, name + " actual selected-skill cast/release/hit")
    if skill_id == "skill.frost_pulse":
        require(effects and all(event["effect_kind"] == "area" for event in effects), name + " actual area output")
        require(any(event["kind"] == "status_applied" for event in trace), name + " actual chill output")
    if skill_id == "skill.arc_chain":
        require(effects and all(event["effect_kind"] == "chain" for event in effects), name + " actual chain output")
    result.append({"case": name, "skill": skill_id, "tick": data["tick"], "actors": data["actor_count"], "alive": data["alive"], "casts": len(casts), "releases": len(releases), "hits": len(hits), "mana_raw": data["mana_raw"], "png_dimensions": [1920, 1080]})
post = json.loads((directory / "post-qa-preservation.json").read_text(encoding="utf-8-sig"))
require(post["source_count"] == 22 and not post["source_mismatches"] and post["game_processes_remaining"] == 0, "Post-QA frozen22 source and renderer shutdown")
report = {"scope": "Ordinary final exported scene with built-in QA controls; separate from native input and performance", "success": not failures, "failures": failures, "cases": result}
output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False))
raise SystemExit(0 if not failures else 1)
