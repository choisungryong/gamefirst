from pathlib import Path
import json,hashlib,importlib.util
r=Path('C:/Project/d2r-combat-baseline');b=r/'plans/chapter1-quality04-20261101-01';o=b/'full24/independent-audit01';assert not o.exists();o.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks={}
old=read(b/'full23/FINAL-SOURCE-FREEZE.json');new=read(b/'full24/FINAL-SOURCE-FREEZE.json');changed=[n for n in old if old[n]!=new[n]];added=[n for n in new if n not in old]
checks['only_assembly_changed']=changed==['chapter1/chapter_one_view.gd'];checks['only_actor24_added']=added==['chapter1/view/chapter_actors_quality24.gd'];checks['root_freeze']=all(sha(r/n)==h for n,h in new.items())
adoption=read(b/'full24/ADOPTION.json');checks['all_preserved_exes']=all(sha(r/n)==h for n,h in adoption['preserved_exes'].items());checks['original_assembly_backup']=sha(Path(adoption['backup'])/changed[0])==old[changed[0]]
for v in ['14','16','17','17b','18','19','20','21','22','23','24']:
 build=read(b/f'full{v}/build/build.json');checks[f'exe{v}']=sha(Path(build['exe']))==build['sha256'];stage=Path(read(b/f'full{v}/build/closure.json')['stage']);checks[f'stage{v}']=all(sha(stage/n)==h for n,h in read(b/f'full{v}/build/staging-manifest.json').items())
for case in ['fixture02','replay01']:
 test=read(b/f'spike24/{case}/source.json')['pins'];checks[case+'_exact_actor_packaged']=all(test[n]==new[n] for n in added);checks[case+'_quiet']=read(b/f'spike24/{case}/gpu-execution.json')=={'exit':0,'stderr_bytes':0}
checks['50_actor_checks']=len(read(b/'spike24/fixture02/RESULT.json')['checks'])==50 and all(read(b/'spike24/fixture02/RESULT.json')['checks'].values());checks['later_replay_core_equal']=read(b/'spike24/replay01/RESULT.json')['same_complete_core']
profile=read(b/'full23/runtime/default-profile-preserved.json');checks['default23_profile_and_journals_unchanged']=all(sha(Path(profile['path'])/n)==h for n,h in profile['pins'].items())
a=read(b/'full23/build/release-policy-smoke.json')['result'];c=read(b/'full24/build/release-policy-smoke.json')['result'];keys=['mode','tick','kills','hero','growth','metrics','chapter','equipped','inventory','elite_reward_uid'];checks['release30sec_core_same']=all(a[k]==c[k] for k in keys)
spec=importlib.util.spec_from_file_location('parser24',r/'tools/build_phase7.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);build=read(b/'full24/build/build.json');checks['pck_reparse']=mod.pck_entries(Path(build['exe']))['entries']==read(b/'full24/build/pck-audit.json')['entries']
(o/'RESULT.json').write_text(json.dumps({'checks':checks,'changed':changed,'added':added,'scope':'Independent preservation/source/stage/PCK/partial core and presenter correspondence. Not whole manual/audio/final3run quality approval.'},ensure_ascii=False,indent=2),encoding='utf-8');print(checks);assert all(checks.values())
