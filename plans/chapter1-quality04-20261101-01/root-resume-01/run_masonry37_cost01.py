from pathlib import Path
import hashlib,json,subprocess,csv,math
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'masonry37/cost01'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=read(B/'masonry37/compare04/SOURCE.json');S=Path(source['stage']);pins=source['pins'];freeze=read(B/'full36/FINAL-SOURCE-FREEZE.json');users=read(B/'full36/USER-PRESERVATION-ADDENDUM02.json')['user_pins'];observer=H/'masonry37_cost01.gd'
def preserved():
 assert all(sha(S/n)==h for n,h in pins.items())
 assert all(sha(R/n)==h for n,h in freeze.items())
 assert all(sha(Path(n))==h for n,h in users.items())
preserved();assert not O.exists();O.mkdir(parents=True)
(O/'SOURCE.json').write_text(json.dumps({'reused_stage':str(S),'source_manifest':str(B/'masonry37/compare04/SOURCE.json'),'observer':str(observer),'observer_sha256':sha(observer),'reservation':'Root granted exclusive CPU/GPU; no other engine/tests during interval. Not a general benchmark.'},indent=2),encoding='utf-8')
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
phases=[('check',['--headless','--check-only','--script',str(observer)])]
for mode in ['37b','37c']:
 phases.append((mode,['--script',str(observer),'--resolution','1920x1080','--disable-vsync','--max-fps','0','--delta-smoothing','disable','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.arc','--chapter1-seed=90131','--masonry-cost-dir='+str(O/mode),'--masonry-cost-world='+mode]))
for label,args in phases:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  command=[engine,'--path',str(S)]+args;p=subprocess.Popen(command,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
  (O/(label+'-launch.json')).write_text(json.dumps({'pid':p.pid,'command':command}),encoding='utf-8');print(label,p.pid,flush=True)
  try:code=p.wait(timeout=180)
  except subprocess.TimeoutExpired:p.terminate();p.wait(timeout=30);raise
 result={'exit':code,'stderr_bytes':(O/(label+'.stderr.txt')).stat().st_size};(O/(label+'-execution.json')).write_text(json.dumps(result),encoding='utf-8');assert result=={'exit':0,'stderr_bytes':0},result
before=read(O/'37b/RESULT.json');after=read(O/'37c/RESULT.json');audits={}
for mode,result in [('37b',before),('37c',after)]:
 with (O/mode/'frames.csv').open(newline='') as f:rows=[{k:int(v) for k,v in r.items()} for r in csv.DictReader(f)]
 intervals=[r['interval_us'] for r in rows];ordered=sorted(intervals)
 assert all(v>0 for v in intervals) and sum(intervals)==result['sample_us'] and len(rows)==result['sample_count']
 assert result['raw_sha256']==sha(O/mode/'frames.csv') and sum(not r['focused'] for r in rows)==result['unfocused_frames']
 assert ordered[math.ceil(len(ordered)*.95)-1]/1000==result['p95_ms']
 audits[mode]={k:result[k] for k in ['p95_ms','p99_ms','max_ms','draw_calls_median','sample_count','unfocused_frames','sample_us']}
checks={'same_complete_core':before['same_complete_core'] and after['same_complete_core'] and before['snapshot']==after['snapshot'],'same_settings':before['settings']==after['settings'],'actual1080p':before['actual_after']==after['actual_after']==[1920,1080],'both_focused':before['unfocused_frames']==after['unfocused_frames']==0}
preserved();assert all(checks.values()),checks
(O/'COMPARISON.json').write_text(json.dumps({'checks':checks,'audits':audits,'p95_ratio':after['p95_ms']/before['p95_ms'],'scope':'Exclusive static2+10s1run37b/37c, unchanged9000tick Core36; regression screen only, not formal dynamic1080p3x. Prior03static cost exploratory due possible headless overlap.'},indent=2),encoding='utf-8');print('MASONRY37 COST01 PASS',flush=True)
