from pathlib import Path
import json,shutil,subprocess,hashlib
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'equipment35/layout01';S=Path('C:/Project/game-research/build-staging/chapter1-equipment35-layout01')
assert not O.exists() and not S.exists();O.mkdir(parents=True);S.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=Path(read(B/'full34/build/closure.json')['stage'])
for n,h in read(B/'full34/build/staging-manifest.json').items():
 assert sha(old/n)==h
 p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
for n in ['chapter1/view/equipment_sigil_quality35.gd','chapter1/view/chapter_hud_quality35.gd']+[str(p.relative_to(R)) for p in (R/'chapter1/art/equipment_icons35').glob('*.svg')]:
 p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
shutil.copy2(Path(__file__).parent/'equipment35_layout.gd',S/'check35.gd')
pins={str(p.relative_to(S)):sha(p) for p in S.rglob('*') if p.is_file()};(O/'SOURCE.json').write_text(json.dumps({'stage':str(S),'pins':pins},indent=2),encoding='utf-8')
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://check35.gd']),('gpu',['--script','res://check35.gd','--resolution','1920x1080','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131'])]:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  cmd=[engine,'--path',str(S)]+args;p=subprocess.Popen(cmd,stdout=out,stderr=err);(O/(label+'-launch.json')).write_text(json.dumps({'pid':p.pid,'command':cmd}));code=p.wait(timeout=180)
 result={'exit':code,'stderr_bytes':(O/(label+'.stderr.txt')).stat().st_size};(O/(label+'-execution.json')).write_text(json.dumps(result));print(label,result,flush=True);assert result=={'exit':0,'stderr_bytes':0}
shutil.copy2(S/'result35.json',O/'RESULT.json')
shutil.copytree(S/'shots35',O/'shots')
print('LAYOUT CAPTURES READY; REVIEW PENDING',flush=True)
