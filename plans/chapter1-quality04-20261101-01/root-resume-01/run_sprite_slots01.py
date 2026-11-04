from pathlib import Path
import json,hashlib,shutil,subprocess,importlib.util
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=B/'root-resume-01';O=B/'sprite-slots01';S=Path('C:/Project/game-research/build-staging/chapter1-sprite-slots01');assert not O.exists() and not S.exists();O.mkdir();S.mkdir();read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();sp=importlib.util.spec_from_file_location('spriteroles',R/'tools/sprite_pipeline/roles.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
assets={role:B/f'sprite-pipeline01/assets/{role}-demo/manifest.json' for role in m.ROLES};m.build({'walker':assets['walker']},{'walker':2},O/'registry-walker.json');m.build(assets,{role:2 for role in m.ROLES},O/'registry-all.json')
rejected={}
for name,bindings,releases in [('role-mismatch',{'ranged':assets['walker']},{'ranged':2}),('missing-release',{'walker':assets['walker']},{}),('release-outside',{'walker':assets['walker']},{'walker':99})]:
 try:m.build(bindings,releases,O/(name+'.json'));rejected[name]=False
 except ValueError:rejected[name]=not (O/(name+'.json')).exists()
assert all(rejected.values());(O/'REGISTRY-NEGATIVE.json').write_text(json.dumps(rejected,indent=2))
old=Path(read(B/'full30/build/closure.json')['stage'])
for n,h in read(B/'full30/build/staging-manifest.json').items():
 assert sha(old/n)==h;p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
for name in ['sprite_asset_presenter.gd','sprite_asset_presenter_v2.gd','sprite_role_registry.gd','sprite_role_actors_preview.gd']:shutil.copy2(R/'chapter1/presentation'/name,S/'chapter1/presentation'/name)
shutil.copytree(B/'sprite-pipeline01/assets',S/'plans/chapter1-quality04-20261101-01/sprite-pipeline01/assets')
for name in ['registry-walker.json','registry-all.json']:
 p=S/'plans/chapter1-quality04-20261101-01/sprite-slots01'/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(O/name,p)
shutil.copy2(H/'sprite_slots_probe.gd',S/'probe.gd');pins={str(p.relative_to(S)).replace('\\','/'):sha(p) for p in S.rglob('*') if p.is_file()};(O/'source.json').write_text(json.dumps(dict(stage=str(S),pins=pins),indent=2));engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
phases=[('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://probe.gd'])]
for surface in ['headless','gpu']:
 for selection in ['walker','all']:
  phases.append((surface+'-'+selection,(['--headless'] if surface=='headless' else ['--resolution','1920x1080'])+['--script','res://probe.gd','--fixed-fps','60','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--slot-dir='+str(O/(surface+'-'+selection)),'--slot-selection='+selection]))
for label,args in phases:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  cmd=[engine,'--path',str(S)]+args;p=subprocess.Popen(cmd,stdout=out,stderr=err);(O/(label+'-launch.json')).write_text(json.dumps(dict(pid=p.pid,command=cmd),indent=2));print(label,p.pid,flush=True);code=p.wait(timeout=210)
 result=dict(exit=code,stderr_bytes=(O/(label+'.stderr.txt')).stat().st_size);(O/(label+'-execution.json')).write_text(json.dumps(result));assert result==dict(exit=0,stderr_bytes=0),result
assert all(sha(S/n)==h for n,h in pins.items());assert all(sha(R/n)==h for n,h in read(B/'full30/FINAL-SOURCE-FREEZE.json').items());print('SPRITE ROLE COMBAT PREVIEW COMPLETE; REVIEW PENDING',flush=True)
