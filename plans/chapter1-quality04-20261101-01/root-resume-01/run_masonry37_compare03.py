"""Fresh37b static comparison; preserve interrupted02 and all product36 pins."""
from pathlib import Path
import hashlib,json,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline')
B=R/'plans/chapter1-quality04-20261101-01'
H=Path(__file__).parent
O=B/'masonry37/compare03'
S=Path('C:/Project/game-research/build-staging/chapter1-masonry37-compare03')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not O.exists() and not S.exists()
O.mkdir(parents=True);S.mkdir()
old=Path(read(B/'full36/build/closure.json')['stage'])
source_freeze=read(B/'full36/FINAL-SOURCE-FREEZE.json')
users=read(B/'full36/USER-PRESERVATION-ADDENDUM02.json')['user_pins']
partial=Path('C:/Project/game-research/build-staging/chapter1-masonry37-compare02')
partial_pins={str(p.relative_to(partial)):sha(p) for p in partial.rglob('*') if p.is_file()}
def preserved():
    assert all(sha(R/n)==h for n,h in source_freeze.items())
    assert all(sha(Path(n))==h for n,h in users.items())
    assert {str(p.relative_to(partial)):sha(p) for p in partial.rglob('*') if p.is_file()}==partial_pins
preserved()
for n,h in read(B/'full36/build/staging-manifest.json').items():
    assert sha(old/n)==h
    p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
for name in ['chapter_world_quality37.gd','chapter_world_quality37b.gd']:
    shutil.copy2(R/'chapter1/view'/name,S/'chapter1/view'/name)
observer=(H/'masonry37_compare.gd').read_text(encoding='utf-8')
observer=observer.replace(' var file=FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE);', ''' # Same static Core36 state and final normal hero camera; bounded wall interval comparison.
 # Time.get_ticks_usec monotonic clock: docs.godotengine.org/en/4.5/classes/class_time.html
 var warm_start: int=Time.get_ticks_usec()
 while Time.get_ticks_usec()-warm_start<2000000:await process_frame
 var intervals: Array[int]=[]
 var sample_start: int=Time.get_ticks_usec()
 var previous: int=sample_start
 while Time.get_ticks_usec()-sample_start<10000000:
  await process_frame
  var now: int=Time.get_ticks_usec();intervals.append(now-previous);previous=now
 intervals.sort()
 var cost: Dictionary={"sample_count":intervals.size(),"sample_us":previous-sample_start,"warmup_us":2000000,"p95_ms":float(intervals[maxi(0,ceili(intervals.size()*.95)-1)])/1000.0,"p99_ms":float(intervals[maxi(0,ceili(intervals.size()*.99)-1)])/1000.0,"max_ms":float(intervals[-1])/1000.0,"scope":"Frozen9000tick normal hero camera;2s warmup+10s static render wall intervals1run each. Not dynamic final formal focused performance."}
 same=same and frozen==view.run.snapshot()
 var file=FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE);''')
observer=observer.replace('"world":variant,','"world":variant,"static_render_cost":cost,')
(S/'compare37.gd').write_text(observer,encoding='utf-8')
(O/'observer.gd').write_text(observer,encoding='utf-8')
pins={str(p.relative_to(S)):sha(p) for p in S.rglob('*') if p.is_file()}
(O/'SOURCE.json').write_text(json.dumps({'stage':str(S),'pins':pins,'preserved_partial02':partial_pins,'preservation_addendum':'USER-PRESERVATION-ADDENDUM02.json'},indent=2),encoding='utf-8')
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
phases=[('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://compare37.gd'])]
for mode in ['31d','37b']:
    phases.append((mode,['--script','res://compare37.gd','--resolution','1920x1080','--disable-vsync','--max-fps','0','--delta-smoothing','disable','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.arc','--chapter1-seed=90131','--masonry37-dir='+str(O/mode),'--masonry37-world='+mode]))
for label,args in phases:
    with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
        command=[engine,'--path',str(S)]+args
        process=subprocess.Popen(command,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
        (O/(label+'-launch.json')).write_text(json.dumps({'pid':process.pid,'command':command}),encoding='utf-8')
        print(label,process.pid,flush=True)
        try:code=process.wait(timeout=180)
        except subprocess.TimeoutExpired:
            process.terminate();process.wait(timeout=30);raise
    result={'exit':code,'stderr_bytes':(O/(label+'.stderr.txt')).stat().st_size}
    (O/(label+'-execution.json')).write_text(json.dumps(result),encoding='utf-8')
    assert result=={'exit':0,'stderr_bytes':0},result
before=read(O/'31d/RESULT.json');after=read(O/'37b/RESULT.json')
checks={'same_full_core':before['snapshot']==after['snapshot'],'same_all_anchors':before['anchors']==after['anchors'],'same_batch_instance_counts':[v['instances'] for v in before['batches']]==[v['instances'] for v in after['batches']],'core_held':before['same_core_after_views'] and after['same_core_after_views']}
assert all(checks.values())
assert all(sha(S/n)==h for n,h in pins.items());preserved()
(O/'COMPARISON.json').write_text(json.dumps({'checks':checks,'visual_review_pending':True,'before_static_render_cost':before['static_render_cost'],'after_static_render_cost':after['static_render_cost'],'scope':'Unconnected37b source study. SameCore36; static render sample only, not final dynamic formal. Product36/user23/29/36 and partial02 preserved.'},indent=2),encoding='utf-8')
print('MASONRY37b COMPARE03 PASS; VISUAL REVIEW PENDING',flush=True)
