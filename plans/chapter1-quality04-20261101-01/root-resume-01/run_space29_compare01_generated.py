from pathlib import Path
import hashlib,json,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent
O=B/'space29/compare01';S=Path('C:/Project/game-research/build-staging/chapter1-space29-compare01')
assert not O.exists() and not S.exists();O.mkdir(parents=True);S.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=Path(read(B/'full28/build/closure.json')['stage'])
for n,h in read(B/'full28/build/staging-manifest.json').items():
 assert sha(old/n)==h
 p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
shutil.copy2(R/'chapter1/view/chapter_world_quality29.gd',S/'chapter1/view/chapter_world_quality29.gd')
shutil.copy2(H/'space29_compare.gd',S/'compare.gd')
pins={str(p.relative_to(S)).replace('\\','/'):sha(p) for p in S.rglob('*') if p.is_file()}
(O/'source.json').write_text(json.dumps(dict(stage=str(S),pins=pins),indent=2))
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://compare.gd']),('gpu',['--script','res://compare.gd','--resolution','1920x1080','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131'])]:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  cmd=[engine,'--path',str(S)]+args;p=subprocess.Popen(cmd,stdout=out,stderr=err)
  (O/(label+'-launch.json')).write_text(json.dumps(dict(pid=p.pid,command=cmd),indent=2));print(label,p.pid,flush=True);code=p.wait(timeout=180)
 result=dict(exit=code,stderr_bytes=(O/(label+'.stderr.txt')).stat().st_size)
 (O/(label+'-execution.json')).write_text(json.dumps(result));assert result==dict(exit=0,stderr_bytes=0),result
shutil.copy2(S/'space29-result.json',O/'RESULT.json');shutil.copytree(S/'space29-shots',O/'shots')
assert all(sha(S/n)==h for n,h in pins.items())
assert all(sha(R/n)==h for n,h in read(B/'full28/FINAL-SOURCE-FREEZE.json').items())
print('PASS SPACE27 COMBAT FIXTURE; VISUAL REVIEW PENDING',flush=True)
