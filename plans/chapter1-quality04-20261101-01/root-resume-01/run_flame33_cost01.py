from pathlib import Path
import json,hashlib,shutil,subprocess,math
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=B/'root-resume-01';O=B/'flame33/cost01';S=Path('C:/Project/game-research/build-staging/chapter1-flame33-cost01');assert not O.exists() and not S.exists();O.mkdir();S.mkdir();read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=Path(read(B/'full32/build/closure.json')['stage'])
for n,h in read(B/'full32/build/staging-manifest.json').items():
 assert sha(old/n)==h;p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
for name in ['chapter_elements_quality33.gd','flame_bloom_quality33.gdshader']:shutil.copy2(R/'chapter1/view'/name,S/'chapter1/view'/name)
shutil.copy2(H/'flame33_cost.gd',S/'cost.gd');pins={str(p.relative_to(S)).replace('\\','/'):sha(p) for p in S.rglob('*') if p.is_file()};(O/'source.json').write_text(json.dumps(dict(stage=str(S),pins=pins),indent=2));engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe';phases=[('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://cost.gd'])]
for variant in ['26','33']:phases.append((variant,['--script','res://cost.gd','--resolution','1920x1080','--disable-vsync','--max-fps','0','--delta-smoothing','disable','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.ember','--chapter1-seed=90131','--flame33-dir='+str(O/variant),'--flame33-actor='+variant]))
for label,args in phases:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  cmd=[engine,'--path',str(S)]+args;p=subprocess.Popen(cmd,stdout=out,stderr=err);(O/(label+'-launch.json')).write_text(json.dumps(dict(pid=p.pid,command=cmd),indent=2));print(label,p.pid,flush=True);code=p.wait(timeout=210)
 result=dict(exit=code,stderr_bytes=(O/(label+'.stderr.txt')).stat().st_size);(O/(label+'-execution.json')).write_text(json.dumps(result));assert result==dict(exit=0,stderr_bytes=0),result
rows=[]
for variant in ['26','33']:
 d=read(O/variant/'RESULT.json');assert d['same_complete_core'];samples=sorted(d['intervals_us']);pct=lambda q:samples[math.ceil(len(samples)*q)-1]/1000
 rows.append(dict(mode=variant,samples=len(samples),seconds=sum(samples)/1e6,start_tick=d['start_tick'],end_tick=d['end_tick'],p50_ms=pct(.5),p95_ms=pct(.95),p99_ms=pct(.99),max_ms=max(samples)/1000,over33ms=sum(v>33333.333 for v in samples),draw_max=max(d['draws']),core_equal=d['same_complete_core'],image=d['image']))
assert all(sha(S/n)==h for n,h in pins.items());assert all(sha(R/n)==h for n,h in read(B/'full32/FINAL-SOURCE-FREEZE.json').items());(O/'COMPARISON.json').write_text(json.dumps(dict(runs=rows,scope='Sequential source normal earned fire16000 FX26/33,2s warmup+10s OS-clock intervals each. No readback inside sample. Ignore-focus uncapped/vsync off. Not actual packaged focused final3runs.'),indent=2));print(json.dumps(rows),flush=True)
