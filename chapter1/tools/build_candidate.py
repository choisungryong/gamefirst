"""Chapter1-only immutable staging/export. Never exports the mixed research tree."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BUILD_ID = "chapter1-c2-candidate-20261031-01"
STAGE = Path("C:/Project/game-research/build-staging") / BUILD_ID
OUTPUT = ROOT / "builds/chapter1" / BUILD_ID
PROOF = ROOT / "plans/chapter1-c2-20261031-01/package-candidate01"
ENGINE = Path("C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, data):
    assert not path.exists(), f"Preserve prior evidence: {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

def runtime_paths():
    names = {"chapter1/Chapter1.tscn", "chapter1/chapter_view.gd", "chapter1/data/growth.json",
             "combat/combat_resolver.gd", "combat/stat_block.gd", "presentation/expedition_audio.gd"}
    names.update("chapter1/core/"+s+".gd" for s in ("combat_run", "growth_catalog", "run_growth"))
    names.update("chapter1/view/"+s+".gd" for s in ("cloister_world", "cloister_actors", "cloister_effects", "cloister_hud"))
    names.update("chapter1/view/"+s+".gdshader" for s in ("comet", "impact", "foot_shadow"))
    for role in ("hero", "walker", "ranged", "charger", "elite"):
        names.update("chapter1/art/actors/"+role+suffix for suffix in (".png", "_actions.png", ".json"))
    names.add("chapter1/art/terrain/cloister_ground_v01.png")
    names.update("assets/expedition/audio/"+s+".wav" for s in ("fire", "cold", "lightning", "impact", "hurt", "death", "drop", "pickup", "equip", "ambience"))
    for name in names: assert (ROOT/name).is_file(), name
    return sorted(names)

def main():
    assert not any(p.exists() for p in (STAGE, OUTPUT, PROOF)), "Choose a new build ID; preserve existing candidates"
    paths = runtime_paths()
    for folder in (STAGE, OUTPUT, PROOF):folder.mkdir(parents=True)
    source = {p:sha(ROOT/p) for p in paths}
    for p in paths:
        target=STAGE/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/p,target)
    project=(ROOT/"project.godot").read_text(encoding="utf-8")
    assert project.count('run/main_scene="res://Baseline.tscn"')==1
    project=project.replace('run/main_scene="res://Baseline.tscn"','run/main_scene="res://chapter1/Chapter1.tscn"')
    project=project.replace('config/name="D2R Combat Baseline"','config/name="Ashen Cloister Chapter1 C2"\nconfig/use_custom_user_dir=true\nconfig/custom_user_dir_name="AshenCloisterChapter1C2"')
    (STAGE/"project.godot").write_text(project,encoding="utf-8")
    resources=["res://"+p for p in paths if Path(p).suffix in (".gd",".gdshader",".tscn",".png",".wav")]
    preset=(ROOT/"export_presets.cfg").read_text(encoding="utf-8")
    preset=preset.replace('name="Windows Desktop"','name="Chapter1 Windows"').replace('export_filter="all_resources"','export_filter="selected_resources"\nexport_files=PackedStringArray('+', '.join(json.dumps(p) for p in resources)+')')
    preset=preset.replace('include_filter="assets/licenses/*.txt,game_data/*.json"','include_filter="chapter1/data/*.json,chapter1/art/actors/*.json"')
    (STAGE/"export_presets.cfg").write_text(preset,encoding="utf-8")
    staged={p:sha(STAGE/p) for p in paths+["project.godot","export_presets.cfg"]}
    write(PROOF/"source-manifest.json",source)
    write(PROOF/"staging-manifest.json",staged)
    write(PROOF/"closure.json",{"build_id":BUILD_ID,"stage":str(STAGE),"output":str(OUTPUT),"runtime_source_files":paths,"original_project_sha256":sha(ROOT/"project.godot"),"scope":"90-second representative encounter candidate, not completed 5-8 minute chapter or quality pass"})
    exe=OUTPUT/"AshenCloister-Chapter1.exe"
    commands=[("import",[str(ENGINE),"--headless","--path",str(STAGE),"--editor","--import"]),
              ("export",[str(ENGINE),"--headless","--path",str(STAGE),"--export-release","Chapter1 Windows",str(exe)])]
    for label,command in commands:
        with (PROOF/(label+".log")).open("wb") as log:
            result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
        write(PROOF/(label+"-exit.json"),{"command":command,"exit_code":result.returncode})
        assert result.returncode==0, label+" failed; inspect preserved log"
    assert source=={p:sha(ROOT/p) for p in paths}, "Workspace changed during export"
    assert staged=={p:sha(STAGE/p) for p in staged}, "Staging source changed during export"
    # Reuse the already audited Godot4.5.1 embedded-PCK parser, without executing its CLI.
    sys.dont_write_bytecode=True
    spec=importlib.util.spec_from_file_location("phase7_pck_parser",ROOT/"tools/build_phase7.py")
    parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
    package=parser.pck_entries(exe)
    packed={r["path"].removeprefix("res://"):r for r in package["entries"]}
    for p in paths:
        expected=p+".import" if Path(p).suffix in (".png",".wav") else p+".remap" if Path(p).suffix in (".gd",".tscn") else p
        assert expected in packed or (p.endswith(".gdshader") and p+".remap" in packed), "Required dynamic resource omitted: "+expected
        if p.endswith(".json"):assert packed[p]["sha256"]==source[p], "JSON differs from source: "+p
    forbidden=("evidence/","research/","tests/","tools/","Baseline.tscn","baseline_view","firebolt-sheet","battle_mage_walk_4x4_v01")
    bad=[p for p in packed if any(term.lower() in p.lower() for term in forbidden)]
    assert not bad,bad
    package.update({"exe_sha256":sha(exe),"forbidden_matches":bad,"success":True,"scope":"PCK closure/checksums only; runtime, UI, performance and art quality require separate verification"})
    write(PROOF/"pck-audit.json",package)
    write(PROOF/"build.json",{"exe":str(exe),"sha256":sha(exe),"bytes":exe.stat().st_size,"entry_count":len(packed),"source_count":len(paths),"stage":str(STAGE),"entrypoint":"res://chapter1/Chapter1.tscn","scope":"C2 candidate; quality approval remains open"})
    (OUTPUT/"RUN.ko.md").write_text("# 잿빛 회랑 · Chapter1 C2 후보\n\nAshenCloister-Chapter1.exe를 실행하세요. 약 90초의 대표 전투 구간이며 목표인 5–8분짜리 1장 전체 완성본은 아닙니다.\n\n- WASD 또는 마우스 좌클릭: 이동\n- Space: 회피 · 기술은 자동 시전\n- 성장 화면에서 강화 선택\n- I: 장비 확인·비교·장착\n- Esc: 정지·재개 · M: 음소거 · R: 결과 화면에서 재도전\n\n70초에 등장하는 회랑 수호자를 실제로 처치하면 승리합니다. 시간만 지나서 승리하지 않습니다. 장비와 성장 상태는 이번 플레이에서만 유지되며 저장 기능은 없습니다. 기존 실행 파일이나 세이브를 읽거나 변경하지 않습니다.\n\n독립 제작한 2.5D 스프라이트와 전투 규칙을 사용합니다. 방향별 행동, 지형·소품·효과·음향의 최종 품질과 성능은 계속 검토 중입니다. SACRATA 수준의 완성 품질을 통과했다는 뜻은 아닙니다.\n",encoding="utf-8")
    print(json.dumps({"success":True,"exe":str(exe),"proof":str(PROOF),"sha256":sha(exe)}))

if __name__=="__main__":main()
