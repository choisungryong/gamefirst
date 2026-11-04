from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'loot33/compare01';S=Path('C:/Project/game-research/build-staging/chapter1-loot33-compare01');assert not O.exists() and not S.exists();O.mkdir(parents=True);S.mkdir();read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=Path(read(B/'full32/build/closure.json')['stage'])
for n,h in read(B/'full32/build/staging-manifest.json').items():
 assert sha(old/n)==h;p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
for n in ['chapter_elements_quality33.gd','flame_bloom_quality33.gdshader','chapter_elements_quality33b.gd']:shutil.copy2(R/'chapter1/view'/n,S/'chapter1/view'/n)
shutil.copy2(H/'loot33_compare.gd',S/'compare.gd');pins={str(p.relative_to(S)).replace('\\','/'):sha(p) for p in S.rglob('*') if p.is_file()};(O/'source.json').write_text(json.dumps(dict(stage=str(S),pins=pins),indent=2));engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe';phases=[('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://compare.gd'])]
for variant in ['26','33b']:phases.append((variant,['--script','res://compare.gd','--resolution','1920x1080','--fixed-fps','60','--','--chapter1-profile-off','--chapter1-start','--chapter1-primary=chapter1.skill.ember','--chapter1-seed=90131','--loot33-dir='+str(O/variant),'--loot33-fx='+variant]))
for label,args in phases:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  cmd=[engine,'--path',str(S)]+args;p=subprocess.Popen(cmd,stdout=out,stderr=err);(O/(label+'-launch.json')).write_text(json.dumps(dict(pid=p.pid,command=cmd),indent=2));print(label,p.pid,flush=True);code=p.wait(timeout=180)
 d=dict(exit=code,stderr_bytes=(O/(label+'.stderr.txt')).stat().st_size);(O/(label+'-execution.json')).write_text(json.dumps(d));assert d==dict(exit=0,stderr_bytes=0),d
before=read(O/'26/RESULT.json');after=read(O/'33b/RESULT.json');checks=dict(before_passed=before['passed'],after_passed=after['passed'],same_complete_normal_core=before['normal_core']==after['normal_core'],same_normal_tick=before['normal_tick']==after['normal_tick'],stage_immutable=all(sha(S/n)==h for n,h in pins.items()),root32_immutable=all(sha(R/n)==h for n,h in read(B/'full32/FINAL-SOURCE-FREEZE.json').items()))
(O/'COMPARISON.json').write_text(json.dumps(dict(passed=all(checks.values()),checks=checks,scope='Normal earned three rarity checkpoint plus four-rarity presentation fixture; unique fixture is not natural unique drop.'),indent=2));print(checks,flush=True);assert all(checks.values())
