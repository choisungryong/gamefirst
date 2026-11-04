from pathlib import Path
import json,hashlib,shutil,subprocess,math
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'crowd30/cost02';S=Path('C:/Project/game-research/build-staging/chapter1-crowd30-cost02');assert not O.exists() and not S.exists();O.mkdir(parents=True);S.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=Path(read(B/'full29/build/closure.json')['stage'])
for n,h in read(B/'full29/build/staging-manifest.json').items():
 assert sha(old/n)==h
 p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
shutil.copy2(R/'chapter1/view/chapter_actors_quality30c.gd',S/'chapter1/view/chapter_actors_quality30c.gd');shutil.copy2(H/'crowd30_cost.gd',S/'cost.gd')
pins={str(p.relative_to(S)).replace('\\','/'):sha(p) for p in S.rglob('*') if p.is_file()};(O/'source.json').write_text(json.dumps(dict(stage=str(S),pins=pins),indent=2))
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
phases=[('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://cost.gd'])]
for variant in ['29','30c']:phases.append((variant,['--script','res://cost.gd','--resolution','1920x1080','--disable-vsync','--max-fps','0','--delta-smoothing','disable','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.ember','--chapter1-seed=90131','--crowd30-dir='+str(O/variant),'--crowd30-actor='+variant]))
for label,args in phases:
 with (O/(label+'.stdout.txt')).open('xb') as stdout,(O/(label+'.stderr.txt')).open('xb') as stderr:
  cmd=[engine,'--path',str(S)]+args;p=subprocess.Popen(cmd,stdout=stdout,stderr=stderr);(O/(label+'-launch.json')).write_text(json.dumps(dict(pid=p.pid,command=cmd),indent=2));print(label,p.pid,flush=True);code=p.wait(timeout=180)
 d=dict(exit=code,stderr_bytes=(O/(label+'.stderr.txt')).stat().st_size);(O/(label+'-execution.json')).write_text(json.dumps(d));assert d==dict(exit=0,stderr_bytes=0),d
rows=[]
for variant in ['29','30c']:
 d=read(O/variant/'RESULT.json');assert d['same_complete_core'];s=sorted(d['intervals_us']);p=lambda q:s[math.ceil(len(s)*q)-1]/1000
 rows.append(dict(actor=variant,samples=len(s),sample_seconds=sum(s)/1e6,start_tick=d['start_tick'],end_tick=d['end_tick'],p50_ms=p(.5),p95_ms=p(.95),p99_ms=p(.99),max_ms=max(s)/1000,over16ms=sum(x>16666.667 for x in s),over33ms=sum(x>33333.333 for x in s),max_draws=max(d['draws']),core_equal=d['same_complete_core'],image=d['image']))
assert all(sha(S/n)==h for n,h in pins.items());assert all(sha(R/n)==h for n,h in read(B/'full29/FINAL-SOURCE-FREEZE.json').items())
(O/'COMPARISON.json').write_text(json.dumps(dict(runs=rows,scope='Two sequential source development10s OS-clock tests,2s warmup. Not final focused packaged performance3runs. Percentiles nearest-rank.'),indent=2));print(json.dumps(rows),flush=True)
