from pathlib import Path
import json,hashlib,importlib.util
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full21/independent-audit01';assert not O.exists();O.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(B/'full20/FINAL-SOURCE-FREEZE.json');new=read(B/'full21/FINAL-SOURCE-FREEZE.json');checks={}
changes=sorted(n for n in old if old[n]!=new[n]);added=sorted(n for n in new if n not in old)
checks['scene_and_actor_assembly_only']=changes==sorted(['chapter1/ChapterOne.tscn','chapter1/chapter_one_view.gd'])
checks['two_sources_added']=added==sorted(['chapter1/chapter_one_input21.gd','chapter1/view/chapter_actors_quality21.gd'])
checks['root21_freeze']=all(sha(R/n)==h for n,h in new.items())
backup=Path(read(B/'full21/ADOPTION.json')['backup']);checks['original20_scene_assembly_preserved']=all(sha(backup/n)==old[n] for n in changes)
for version in ['14','16','17','17b','18','19','20','21']:
 build=read(B/('full'+version+'/build/build.json'));checks['exe'+version+'_pin']=sha(Path(build['exe']))==build['sha256']
 stage=Path(read(B/('full'+version+'/build/closure.json'))['stage']);pins=read(B/('full'+version+'/build/staging-manifest.json'));checks['stage'+version+'_pins']=all(sha(stage/n)==h for n,h in pins.items())
checks['tested_actor_packaged']=read(B/'roles21/fixture02/source.json')['pins']['chapter1/view/chapter_actors_quality21.gd']==new['chapter1/view/chapter_actors_quality21.gd']
checks['tested_input_packaged']=read(B/'input21/fixture02/source.json')['pins']['chapter1/chapter_one_input21.gd']==new['chapter1/chapter_one_input21.gd']
checks['role23_pass']=len(read(B/'roles21/fixture02/RESULT.json')['checks'])==23 and all(read(B/'roles21/fixture02/RESULT.json')['checks'].values())
checks['input14_pass']=len(read(B/'input21/fixture02/RESULT.json')['checks'])==14 and all(read(B/'input21/fixture02/RESULT.json')['checks'].values())
native=read(B/'full21/runtime/native-input01/RESULT.json')['records'];checks['actual_native_later_zones']=len(native)==2 and {r['zone'] for r in native}=={1,2} and all(r['correct_target'] and r['moved_toward'] for r in native)
checks['native_quiet']=read(B/'full21/runtime/native-input01/execution.json')=={'exit':0,'stderr_bytes':0}
a=read(B/'full20/build/release-policy-smoke.json')['result'];b=read(B/'full21/build/release-policy-smoke.json')['result'];keys=['mode','tick','kills','hero','growth','metrics','chapter','equipped','inventory','elite_reward_uid'];checks['release30sec_same10']=all(a[k]==b[k] for k in keys)
spec=importlib.util.spec_from_file_location('parser21',R/'tools/build_phase7.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);build=read(B/'full21/build/build.json');checks['pck_reparse']=mod.pck_entries(Path(build['exe']))['entries']==read(B/'full21/build/pck-audit.json')['entries']
result={'checks':checks,'source_changes':changes,'source_added':added,'scope':'Independent source/stage/EXE/PCK/preserved candidates and actual later-zone mouse fixture audit. Normal30simsec policy correspondence; not full21 whole/manual/audio/default-save/final3run quality approval.'}
(O/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');assert all(checks.values());print(json.dumps({'passed':len(checks),'all':all(checks.values())}),flush=True)
