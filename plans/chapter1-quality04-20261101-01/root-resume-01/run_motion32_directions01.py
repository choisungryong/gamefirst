from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'motion32/directions01';S=Path('C:/Project/game-research/build-staging/chapter1-motion32-directions01');assert not O.exists() and not S.exists();O.mkdir();S.mkdir();read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=Path(read(B/'full31/build/closure.json')['stage'])
for n,h in read(B/'full31/build/staging-manifest.json').items():
 assert sha(old/n)==h;p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
shutil.copy2(R/'chapter1/view/chapter_actors_quality32b.gd',S/'chapter1/view/chapter_actors_quality32b.gd');shutil.copy2(H/'motion32_directions.gd',S/'directions.gd');pins={str(p.relative_to(S)).replace('\\','/'):sha(p) for p in S.rglob('*') if p.is_file()};(O/'source.json').write_text(json.dumps(dict(stage=str(S),pins=pins),indent=2),encoding='utf-8');engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
phases=[('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://directions.gd'])]
for mode in ['headless','gpu']:phases.append((mode,(['--headless'] if mode=='headless' else ['--resolution','1920x1080'])+['--script','res://directions.gd','--fixed-fps','60','--','--chapter1-profile-off','--chapter1-start','--chapter1-primary=chapter1.skill.ember','--chapter1-seed=90131','--directions-dir='+str(O/mode)]))
for label,args in phases:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  cmd=[engine,'--path',str(S)]+args;p=subprocess.Popen(cmd,stdout=out,stderr=err);(O/(label+'-launch.json')).write_text(json.dumps(dict(pid=p.pid,command=cmd),indent=2));print(label,p.pid,flush=True);code=p.wait(timeout=180)
 d=dict(exit=code,stderr_bytes=(O/(label+'.stderr.txt')).stat().st_size);(O/(label+'-execution.json')).write_text(json.dumps(d));assert d==dict(exit=0,stderr_bytes=0),d
assert all(sha(S/n)==h for n,h in pins.items());print('DIRECTIONS COMPLETE',flush=True)
