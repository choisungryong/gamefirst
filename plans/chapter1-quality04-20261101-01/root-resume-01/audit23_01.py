from pathlib import Path
import json,hashlib,importlib.util
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full23/independent-audit01';assert not O.exists();O.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(B/'full22/FINAL-SOURCE-FREEZE.json');new=read(B/'full23/FINAL-SOURCE-FREEZE.json');checks={}
changes=sorted(n for n in old if old[n]!=new[n]);added=sorted(n for n in new if n not in old)
checks['assembly_only_changed']=changes==['chapter1/chapter_one_view.gd']
checks['one_hud_source_added']=added==['chapter1/view/chapter_hud_quality23.gd']
checks['root23_freeze']=all(sha(R/n)==h for n,h in new.items())
backup=Path(read(B/'full23/ADOPTION.json')['backup']);checks['original22_assembly_preserved']=sha(backup/changes[0])==old[changes[0]]
for version in ['14','16','17','17b','18','19','20','21','22','23']:
 build=read(B/('full'+version+'/build/build.json'));checks['exe'+version+'_pin']=sha(Path(build['exe']))==build['sha256']
 stage=Path(read(B/('full'+version+'/build/closure.json'))['stage']);pins=read(B/('full'+version+'/build/staging-manifest.json'));checks['stage'+version+'_pins']=all(sha(stage/n)==h for n,h in pins.items())
tested=read(B/'hud23/fixture01/source.json')['pins'];checks['tested_sources_packaged']=all(tested[n]==new[n] for n in added)
hud=read(B/'hud23/fixture01/RESULT.json');checks['nine_hud_states_fit_core_restored']=hud['same_complete_core_restored'] and len(hud['records'])==9 and all(v['fits'] and v['two_lines'] and v['inside_viewport'] for v in hud['records'])
checks['hud_quiet']=read(B/'hud23/fixture01/gpu-execution.json')=={'exit':0,'stderr_bytes':0}
save=read(B/'full23/runtime/default-save02/RESULT.json');checks['actual_default_saved34']=save['profile_path']=='user://chapter-one-profile-v1.json' and save['profile_available'] and len(save['profile']['items'])==34 and save['profile']['revision']==1 and save['profile']['completed_runs']==1
checks['default_preflight_fresh']=not read(B/'full23/runtime/default-save02/preflight.json')['exists']
checks['default_save_quiet']=read(B/'full23/runtime/default-save02/native-execution.json')=={'exit':0,'stderr_bytes':0}
for reload in ['default-reload01','default-reload02']:
 proof=read(B/'full23/runtime'/reload/'RESULT.json');checks[reload+'_ring_imported']=proof['loaded_items']==34 and proof['after_revision']==2 and proof['selected']=={'ring':4} and 'ring' in proof['run_gear']['equipped']
 checks[reload+'_quiet']=read(B/'full23/runtime'/reload/'execution.json')=={'exit':0,'stderr_bytes':0}
checks['second_reload_bytes_unchanged']=read(B/'full23/runtime/default-reload02/RESULT.json')['unchanged_profile_bytes']
a=read(B/'full22/build/release-policy-smoke.json')['result'];b=read(B/'full23/build/release-policy-smoke.json')['result'];keys=['mode','tick','kills','hero','growth','metrics','chapter','equipped','inventory','elite_reward_uid'];checks['release30sec_same10']=all(a[k]==b[k] for k in keys)
spec=importlib.util.spec_from_file_location('parser22',R/'tools/build_phase7.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);build=read(B/'full23/build/build.json');checks['pck_reparse']=mod.pck_entries(Path(build['exe']))['entries']==read(B/'full23/build/pck-audit.json')['entries']
result={'checks':checks,'source_changes':changes,'source_added':added,'scope':'Source/stage/EXE/PCK preservation and partial presentation/core correspondence. Includes actual23 default user path happy-path save/native equip/restart proof. Not whole manual/audio/all save failure modes/final3run quality approval.'}
(O/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');assert all(checks.values());print(json.dumps({'passed':len(checks),'all':all(checks.values())}),flush=True)
