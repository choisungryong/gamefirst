from pathlib import Path
import json,hashlib,importlib.util
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full20/independent-audit01';assert not O.exists();O.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(B/'full19/FINAL-SOURCE-FREEZE.json');new=read(B/'full20/FINAL-SOURCE-FREEZE.json');checks={}
changes=[n for n in old if old[n]!=new[n]];added=sorted(n for n in new if n not in old)
checks['assembly_only_changed']=changes==['chapter1/chapter_one_view.gd']
checks['three_presenters_added']=added==sorted('chapter1/view/'+n for n in ['chapter_hud_quality20.gd','chapter_actors_quality20.gd','chapter_elements_quality20.gd'])
checks['root20_freeze']=all(sha(R/n)==h for n,h in new.items())
backup=Path(read(B/'full20/ADOPTION.json')['backup']);checks['original19_assembly_preserved']=sha(backup/'chapter1/chapter_one_view.gd')==old['chapter1/chapter_one_view.gd']
for version in ['14','16','17','17b','18','19','20']:
 build=read(B/('full'+version+'/build/build.json'));checks['exe'+version+'_pin']=sha(Path(build['exe']))==build['sha256']
 stage=Path(read(B/('full'+version+'/build/closure.json'))['stage']);pins=read(B/('full'+version+'/build/staging-manifest.json'));checks['stage'+version+'_pins']=all(sha(stage/n)==h for n,h in pins.items())
tested=read(B/'ending20/replay02/source.json')['pins'];checks['tested_presenters_are_packaged']=all(tested[n]==new[n] for n in added)
ending=read(B/'ending20/replay02/RESULT.json');checks['ending17_edges_pass']=len(ending['checks'])==17 and all(ending['checks'].values());checks['ending_complete_core_same']=ending['same_complete_core_as_normal_reference']
checks['source_ending_gpu_quiet']=read(B/'ending20/replay02/gpu-execution.json')=={'exit':0,'stderr_bytes':0}
spec=importlib.util.spec_from_file_location('parser20',R/'tools/build_phase7.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
build=read(B/'full20/build/build.json');checks['pck_reparse']=mod.pck_entries(Path(build['exe']))['entries']==read(B/'full20/build/pck-audit.json')['entries']
first=read(B/'full20/runtime/native-save01/profile-after-first-exit.json');selected=read(B/'full20/runtime/native-save-reload01/profile-after-exit.json');reloaded=read(B/'full20/runtime/native-save-reload02/profile-before-reload.json');after=read(B/'full20/runtime/native-save-reload02/profile-after-exit.json')
checks['qa34_rewards_saved']=first['completed_runs']==1 and len(first['items'])==34 and first['revision']==1
checks['qa_ring_selection_saved']=selected['equipped']=={'ring':4} and selected['revision']==2
checks['qa_selection_survived_restart']=selected==reloaded==after
result={'checks':checks,'source_changes':changes,'source_added':added,'scope':'Root/stage/EXE/PCK/source ending correspondence and isolated QA JSON persistence. Native runners have known QA res-directory/capture errors and are not quiet passes. No full20 whole GPU/manual/audio/default-user-path/final3run claim.'}
(O/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');assert all(checks.values());print(json.dumps({'passed':len(checks),'all':all(checks.values())}),flush=True)
