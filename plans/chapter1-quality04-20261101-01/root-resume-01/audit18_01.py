from pathlib import Path
import json,hashlib,importlib.util
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';OUT=B/'full18/independent-audit01';assert not OUT.exists();OUT.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks={};old=read(B/'full17b/FINAL-SOURCE-FREEZE.json');new=read(B/'full18/FINAL-SOURCE-FREEZE.json')
changes=[n for n in old if old[n]!=new[n]];added=[n for n in new if n not in old]
checks['only_assembly_and_new_world']=changes==['chapter1/chapter_one_view.gd'] and added==['chapter1/view/chapter_world_quality18.gd']
checks['root18_freeze']=all(sha(R/n)==h for n,h in new.items())
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before18-20261102-01')
checks['original17b_assembly_preserved']=sha(backup/'chapter1/chapter_one_view.gd')==old['chapter1/chapter_one_view.gd']
for version in ['14','16','17','17b','18']:
 build=read(B/('full'+version+'/build/build.json'));checks['exe'+version+'_pin']=sha(Path(build['exe']))==build['sha256']
 stage=Path(read(B/('full'+version+'/build/closure.json'))['stage']);pins=read(B/('full'+version+'/build/staging-manifest.json'));checks['stage'+version+'_pins']=all(sha(stage/n)==h for n,h in pins.items())
source=read(B/'ground18/matrix01/RESULT.json');packed=read(B/'full18/runtime/ground-matrix01/RESULT.json');checks['source_packaged36_same']=source['cases']==packed['cases'] and len(packed['cases'])==36
checks['packaged_covers_all_and_core_unchanged']=packed['all_new_floor_covers'] and packed['core_unchanged']
checks['packaged_gpu_quiet']=read(B/'full18/runtime/ground-matrix01/execution.json')=={'exit':0,'stderr_bytes':0}
checks['tested_world_is_packaged_source']=read(B/'ground18/matrix01/source.json')['pins']['chapter1/view/chapter_world_quality18.gd']==new['chapter1/view/chapter_world_quality18.gd']
spec=importlib.util.spec_from_file_location('parser18',R/'tools/build_phase7.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);build=read(B/'full18/build/build.json');checks['pck_reparse']=mod.pck_entries(Path(build['exe']))['entries']==read(B/'full18/build/pck-audit.json')['entries']
spec=importlib.util.spec_from_file_location('package18',B/'full18/package_full18.py');pkg=importlib.util.module_from_spec(spec);spec.loader.exec_module(pkg);preserved=pkg.preservation()
result={'checks':checks,'source_changes':changes,'source_added':added,'selected_historical_preservation':preserved,'scope':'Root/stage/EXE/PCK and source/packaged ground GPU fixture audit. No full18 normalGPU/manual/audio/performance approval.'};(OUT/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');assert all(checks.values());print(json.dumps({'passed':len(checks),'all':all(checks.values())}),flush=True)
