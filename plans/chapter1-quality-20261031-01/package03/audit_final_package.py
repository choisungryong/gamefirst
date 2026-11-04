"""Read-only package audit with new append-only evidence; no GPU or product edits."""
from pathlib import Path
import importlib.util
import re
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("quality03_package", HERE/"package_quality03.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

source = p.read(p.PROOF/"source-manifest.json")
p.check_pins(p.ROOT, source)
p.check_pins(p.STAGE, p.read(p.PROOF/"staging-manifest.json"))
literal_refs = []
for name in source:
    if Path(name).suffix not in (".gd", ".tscn", ".json"):
        continue
    body = (p.ROOT/name).read_text(encoding="utf-8")
    for ref in sorted(set(re.findall(r'res://([^"\s]+\.(?:gdshader|tscn|png|wav|json|gd))(?=["\s])', body))):
        assert ref in source, (name, ref)
        literal_refs.append({"from":name,"to":ref})

old = (p.OLD_STAGE/"chapter1/chapter_view.gd").read_text(encoding="utf-8")
new = (p.STAGE/"chapter1/chapter_view.gd").read_text(encoding="utf-8")
extract = lambda body:re.search(r'func _pilot_input\(\).*?(?=\nfunc )', body, re.S).group(0)
assert extract(old) == extract(new), "Normal-input driver differs from preserved candidate02"
core_paths = [name for name in source if name.startswith("chapter1/core/") or name in (
    "chapter1/data/growth.json", "combat/combat_resolver.gd", "combat/stat_block.gd")]
assert all(p.sha(p.OLD_STAGE/name) == source[name] for name in core_paths)
smoke = p.read(p.PROOF/"packaged-headless-smoke-execution.json")
world = [p.json.loads(line.split("CHAPTER1_WORLD_ART ",1)[1]) for line in smoke["stdout"].splitlines()
         if "CHAPTER1_WORLD_ART " in line]
assert len(world) == 1 and world[0]["raw_texture_fallbacks"] == []
output = {str(path.relative_to(p.OUTPUT)).replace("\\", "/"):p.sha(path)
          for path in p.OUTPUT.rglob("*") if path.is_file()}
p.write(p.PROOF/"final-package-audit.json", {"source_matches":True,"stage_matches":True,
    "runtime70_literal_references":literal_refs,"missing_references":[],
    "old_new_core_files_equal":core_paths,"old_new_normal_driver_equal":True,
    "driver_sha256":p.hashlib.sha256(extract(new).encode("utf-8")).hexdigest(),
    "world_raw_texture_fallbacks":world[0]["raw_texture_fallbacks"],
    "output_manifest":output,"preservation":p.preservation(),
    "scope":"Static literal closure and exact core/driver comparison, selected pins; no GPU or play-quality approval"})
print(p.json.dumps({"success":True,"literal_reference_count":len(literal_refs),"old_new_core_equal":len(core_paths),"old_new_driver_equal":True,"output_files":len(output)}))
