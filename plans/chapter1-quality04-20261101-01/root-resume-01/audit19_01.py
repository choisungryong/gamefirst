from pathlib import Path
import json,hashlib,importlib.util
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full19/independent-audit01';assert not O.exists();O.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(B/'full18/FINAL-SOURCE-FREEZE.json');new=read(B/'full19/FINAL-SOURCE-FREEZE.json');checks={}
changes=[n for n in old if old[n]!=new[n]];added=sorted(n for n in new if n not in old)
checks['assembly_only_changed']=changes==['chapter1/chapter_one_view.gd']
checks['three_actor_files_added']=added==sorted('chapter1/view/'+n for n in ['chapter_actors_demon19.gd','chapter_actors_readable19.gd','chapter_actors_batched19.gd'])
checks['root19_freeze']=all(sha(R/n)==h for n,h in new.items())
backup=Path(read(B/'full19/ADOPTION.json')['backup']);checks['original18_assembly_preserved']=sha(backup/'chapter1/chapter_one_view.gd')==old['chapter1/chapter_one_view.gd']
for version in ['14','16','17','17b','18','19']:
 build=read(B/('full'+version+'/build/build.json'));checks['exe'+version+'_pin']=sha(Path(build['exe']))==build['sha256']
 stage=Path(read(B/('full'+version+'/build/closure.json'))['stage']);pins=read(B/('full'+version+'/build/staging-manifest.json'));checks['stage'+version+'_pins']=all(sha(stage/n)==h for n,h in pins.items())
tested=read(B/'motion19/fixture02/source.json')['pins'];checks['tested_actor_sources_are_packaged']=all(tested[n]==new[n] for n in added)
checks['fixture16_all_pass']=all(read(B/'motion19/fixture02/RESULT.json')['checks'].values())
checks['fixture_gpu_quiet']=read(B/'motion19/fixture02/gpu-execution.json')=={'exit':0,'stderr_bytes':0}
spec=importlib.util.spec_from_file_location('parser19',R/'tools/build_phase7.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
build=read(B/'full19/build/build.json');checks['pck_reparse']=mod.pck_entries(Path(build['exe']))['entries']==read(B/'full19/build/pck-audit.json')['entries']
gpu=read(B/'full19/runtime/gpu-cold01/RESULT.json');checks['gpu_same10']=all(gpu['same10_as_packaged16'].values());checks['actual_shatters840']=gpu['observer']['shatters']==840
checks['actual_gpu_quiet']=read(B/'full19/runtime/gpu-cold01/gpu-execution.json')=={'actual_exit':0,'stderr_bytes':0}
result={'checks':checks,'source_changes':changes,'source_added':added,'scope':'Independent root/stage/EXE/PCK/source-test correspondence and full GPU core/shatter audit; no manual/audio/saveUI/final3run approval.'}
(O/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');assert all(checks.values());print(json.dumps({'passed':len(checks),'all':all(checks.values())}),flush=True)
