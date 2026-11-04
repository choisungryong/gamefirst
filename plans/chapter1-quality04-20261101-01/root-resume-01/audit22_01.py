from pathlib import Path
import json,hashlib,importlib.util
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full22/independent-audit01';assert not O.exists();O.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(B/'full21/FINAL-SOURCE-FREEZE.json');new=read(B/'full22/FINAL-SOURCE-FREEZE.json');checks={}
changes=sorted(n for n in old if old[n]!=new[n]);added=sorted(n for n in new if n not in old)
checks['assembly_only_changed']=changes==['chapter1/chapter_one_view.gd']
checks['three_presentation_sources_added']=added==sorted(['chapter1/view/chapter_world_quality22.gd','chapter1/view/chapter_elements_quality22.gd','chapter1/view/comet_hostile22.gdshader'])
checks['root22_freeze']=all(sha(R/n)==h for n,h in new.items())
backup=Path(read(B/'full22/ADOPTION.json')['backup']);checks['original21_assembly_preserved']=sha(backup/changes[0])==old[changes[0]]
for version in ['14','16','17','17b','18','19','20','21','22']:
 build=read(B/('full'+version+'/build/build.json'));checks['exe'+version+'_pin']=sha(Path(build['exe']))==build['sha256']
 stage=Path(read(B/('full'+version+'/build/closure.json'))['stage']);pins=read(B/('full'+version+'/build/staging-manifest.json'));checks['stage'+version+'_pins']=all(sha(stage/n)==h for n,h in pins.items())
tested=read(B/'space22/replay01/source.json')['pins'];checks['tested_sources_packaged']=all(tested[n]==new[n] for n in added)
for proof in ['hostile22/compare02','hostile22/replay01','space22/compare04','space22/replay01']:
 checks[proof+'_core_same_quiet']=read(B/proof/'RESULT.json')['same_complete_core'] and read(B/proof/'gpu-execution.json')=={'exit':0,'stderr_bytes':0}
checks['masonry_outside_walkable']=read(B/'space22/compare04/RESULT.json')['all_new_masonry_outside_walkable']
a=read(B/'full21/build/release-policy-smoke.json')['result'];b=read(B/'full22/build/release-policy-smoke.json')['result'];keys=['mode','tick','kills','hero','growth','metrics','chapter','equipped','inventory','elite_reward_uid'];checks['release30sec_same10']=all(a[k]==b[k] for k in keys)
spec=importlib.util.spec_from_file_location('parser22',R/'tools/build_phase7.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);build=read(B/'full22/build/build.json');checks['pck_reparse']=mod.pck_entries(Path(build['exe']))['entries']==read(B/'full22/build/pck-audit.json')['entries']
result={'checks':checks,'source_changes':changes,'source_added':added,'scope':'Source/stage/EXE/PCK preservation and partial presentation/core correspondence. Not actual22 whole/manual/audio/default-save/final3run quality approval.'}
(O/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');assert all(checks.values());print(json.dumps({'passed':len(checks),'all':all(checks.values())}),flush=True)
