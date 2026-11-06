"""Resume visual study after disk cleanup; reuse verified04 source stage."""
from pathlib import Path
import hashlib,json,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01'
O=B/'masonry37/compare05';prior=B/'masonry37/compare04'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=read(prior/'SOURCE.json');S=Path(source['stage']);pins=source['pins']
assert not O.exists();O.mkdir(parents=True)
freeze=read(B/'full36/FINAL-SOURCE-FREEZE.json');users=read(B/'full36/USER-PRESERVATION-ADDENDUM02.json')['user_pins']
def preserved():
 assert all(sha(S/n)==h for n,h in pins.items())
 assert all(sha(R/n)==h for n,h in freeze.items())
 assert all(sha(Path(n))==h for n,h in users.items())
 assert sha(R/'chapter1/view/chapter_world_quality37c.gd')==sha(S/'chapter1/view/chapter_world_quality37c.gd')
 assert sha(R/'chapter1/view/chapter_masonry_quality37c.gdshader')==sha(S/'chapter1/view/chapter_masonry_quality37c.gdshader')
preserved()
(O/'SOURCE.json').write_text(json.dumps({'reused_source_stage':str(S),'original_source_manifest':str(prior/'SOURCE.json'),'original_source_manifest_sha256':sha(prior/'SOURCE.json'),'pins':pins,'prior04_disposition':'Interrupted for Cdrive disk-full cleanup; raw/partial capture preserved. Generated caches moved toD, source unchanged. No rerun of completed comparison31d or37b.'},indent=2),encoding='utf-8')
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
phases=[('reimport',['--headless','--editor','--import']),('37c',['--script','res://compare37.gd','--resolution','1920x1080','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.arc','--chapter1-seed=90131','--masonry37-dir='+str(O/'37c'),'--masonry37-world=37c'])]
for label,args in phases:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  command=[engine,'--path',str(S)]+args;p=subprocess.Popen(command,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
  (O/(label+'-launch.json')).write_text(json.dumps({'pid':p.pid,'command':command}),encoding='utf-8');print(label,p.pid,flush=True)
  try:code=p.wait(timeout=180)
  except subprocess.TimeoutExpired:p.terminate();p.wait(timeout=30);raise
 result={'exit':code,'stderr_bytes':(O/(label+'.stderr.txt')).stat().st_size};(O/(label+'-execution.json')).write_text(json.dumps(result),encoding='utf-8');assert result=={'exit':0,'stderr_bytes':0},result
before=read(B/'masonry37/compare03/37b/RESULT.json');after=read(O/'37c/RESULT.json')
checks={'same_full_core':before['snapshot']==after['snapshot'],'same_all_anchors':before['anchors']==after['anchors'],'same_batches':before['batches']==after['batches'],'same_camera_records':before['records']==after['records'],'core_held':before['same_core_after_views'] and after['same_core_after_views'],'proxy_original_materials':len(after['proxy_materials'])==2}
assert all(checks.values());preserved()
(O/'COMPARISON.json').write_text(json.dumps({'checks':checks,'visual_review_pending':True,'reference':str(B/'masonry37/compare03/37b/RESULT.json'),'scope':'37c material-only comparison against37b03 exact fullCore36+camera geometry. No timing measured. Product36/old evidence/user23/29/36 preserved.'},indent=2),encoding='utf-8');print('MASONRY37c COMPARE05 PASS; VISUAL REVIEW PENDING',flush=True)
