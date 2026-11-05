from pathlib import Path
import json,hashlib,subprocess,math
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'balance36/cost01';assert not O.exists();O.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=read(B/'balance36/arc02/SOURCE.json');S=Path(source['stage']);assert all(sha(S/n)==h for n,h in source['pins'].items())
script=H/'balance36_cost.gd';(O/'SOURCE.json').write_text(json.dumps({'reused_stage':str(S),'pins_source':str(B/'balance36/arc02/SOURCE.json'),'observer_sha256':sha(script),'root_remains_candidate35':True},indent=2));engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
phases=[('check',['--headless','--check-only','--script',str(script)])]
for mode in ['legacy','36']:phases.append((mode,['--script',str(script),'--resolution','1920x1080','--disable-vsync','--max-fps','0','--delta-smoothing','disable','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--balance36-dir='+str(O/mode),'--balance36-mode='+mode]))
for label,args in phases:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  cmd=[engine,'--path',str(S)]+args;p=subprocess.Popen(cmd,stdout=out,stderr=err);(O/(label+'-launch.json')).write_text(json.dumps({'pid':p.pid,'command':cmd}));print(label,p.pid,flush=True);code=p.wait(timeout=180)
 result={'exit':code,'stderr_bytes':(O/(label+'.stderr.txt')).stat().st_size};(O/(label+'-execution.json')).write_text(json.dumps(result));assert result=={'exit':0,'stderr_bytes':0},result
rows=[]
for mode in ['legacy','36']:
 d=read(O/mode/'RESULT.json');assert d['same_complete_core'];v=sorted(d['intervals_us']);pct=lambda q:v[math.ceil(len(v)*q)-1]/1000
 rows.append({'mode':mode,'samples':len(v),'seconds':sum(v)/1e6,'start_tick':d['start_tick'],'end_tick':d['end_tick'],'p50_ms':pct(.5),'p95_ms':pct(.95),'p99_ms':pct(.99),'max_ms':max(v)/1000,'over33ms':sum(x>33333.333 for x in v),'draw_max':max(d['draws']),'core_equal':True,'image':d['image']})
assert all(sha(S/n)==h for n,h in source['pins'].items());assert all(sha(R/n)==h for n,h in read(B/'full35/FINAL-SOURCE-FREEZE.json').items())
(O/'COMPARISON.json').write_text(json.dumps({'runs':rows,'scope':'Same Core36 normal earned frost16000 checkpoint; presentation only legacy34b/33b vs36/36,2s warmup+10s OS clock each,1080p uncapped/vsync off/delta smoothing off/ignore-focus/no capture in sample. Not historical product35 vs36 gameplay cost or final focused performance.'},indent=2));print(json.dumps(rows),flush=True)
