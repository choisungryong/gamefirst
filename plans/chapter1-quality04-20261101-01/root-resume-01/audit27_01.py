from pathlib import Path
import hashlib,json,importlib.util
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full27/independent-audit01';assert not O.exists();O.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks={}
old=read(B/'full26/FINAL-SOURCE-FREEZE.json');new=read(B/'full27/FINAL-SOURCE-FREEZE.json')
checks['only_assembly_changed']=[n for n in old if old[n]!=new[n]]==['chapter1/chapter_one_view.gd']
checks['only_hud27_added']=[n for n in new if n not in old]==['chapter1/view/chapter_hud_quality27.gd']
checks['root_freeze']=all(sha(R/n)==h for n,h in new.items())
ad=read(B/'full27/ADOPTION.json');checks['all_prior_exes']=all(sha(R/n)==h for n,h in ad['preserved_exes'].items())
checks['original26_assembly']=sha(Path(ad['backup'])/'chapter1/chapter_one_view.gd')==old['chapter1/chapter_one_view.gd']
for name in ['14','16','17','17b','18','19','20','21','22','23','24','25','25b','26','27']:
 p=B/('full'+name)/'build';closure=read(p/'closure.json');stage=Path(closure['stage']);pins=read(p/'staging-manifest.json')
 checks['immutable_stage_'+name]=all(sha(stage/n)==h for n,h in pins.items())
profile=read(B/'full23/runtime/default-profile-preserved.json');checks['saved_profile_and_journals']=all(sha(Path(profile['path'])/n)==h for n,h in profile['pins'].items())
a=read(B/'full26/build/release-policy-smoke.json')['result'];d=read(B/'full27/build/release-policy-smoke.json')['result'];keys=['mode','tick','kills','hero','growth','metrics','chapter','equipped','inventory','elite_reward_uid'];checks['release30sec_core10same']=all(a[k]==d[k] for k in keys)
for label in ['import','export','packaged-headless-smoke','release-behavior-probe']:
 e=read(B/f'full27/build/{label}-execution.json');checks['quiet_'+label]=e['actual_exit']==0 and not e['stderr']
fixture=B/'hud27/fixture01';f=read(fixture/'RESULT.json');checks['fixture_all_checks']=f['passed'] and all(c['ok'] for c in f['checks']);checks['tested_hud_exact']=sha(R/'chapter1/view/chapter_hud_quality27.gd')==read(fixture/'source.json')['pins']['chapter1/view/chapter_hud_quality27.gd']
actual=B/'full27/runtime/boss-phase01';a=read(actual/'proof/RESULT.json');checks['actual_event_core_message_and_layout']=all(a[n] for n in ['found_actual_boss_phase','message_ok','separated','same_complete_core']);checks['actual_hud_loaded']=a['hud_script']=='res://chapter1/view/chapter_hud_quality27.gd';checks['actual_image1080p']=a['image']==[1920,1080];checks['actual_quiet']=read(actual/'gpu-execution.json')==dict(exit=0,stderr_bytes=0)
build=read(B/'full27/build/build.json');checks['exe_pin']=sha(Path(build['exe']))==build['sha256'];spec=importlib.util.spec_from_file_location('pck27',R/'tools/build_phase7.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);checks['pck_reparse']=module.pck_entries(Path(build['exe']))['entries']==read(B/'full27/build/pck-audit.json')['entries']
(O/'RESULT.json').write_text(json.dumps(dict(checks=checks,passed=all(checks.values()),scope='Preservation, exact adopted HUD, actual boss phase frozen screenshot and core equivalence. Not final manual/audio/performance/whole quality approval.'),indent=2),encoding='utf-8')
print('AUDIT27',len(checks),'checks; failures',[n for n,v in checks.items() if not v]);assert all(checks.values())
