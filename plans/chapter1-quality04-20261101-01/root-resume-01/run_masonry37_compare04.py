"""37c rear-only material study; reuse completed03 reference, no timing claims."""
from pathlib import Path
import hashlib,json,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent
O=B/'masonry37/compare04';S=Path('C:/Project/game-research/build-staging/chapter1-masonry37-compare04')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not O.exists() and not S.exists();O.mkdir(parents=True);S.mkdir()
freeze=read(B/'full36/FINAL-SOURCE-FREEZE.json');users=read(B/'full36/USER-PRESERVATION-ADDENDUM02.json')['user_pins']
partial=Path('C:/Project/game-research/build-staging/chapter1-masonry37-compare02')
partial_pins={str(p.relative_to(partial)):sha(p) for p in partial.rglob('*') if p.is_file()}
before_result=B/'masonry37/compare03/37b/RESULT.json';before_hash=sha(before_result)
def preserved():
 assert all(sha(R/n)==h for n,h in freeze.items())
 assert all(sha(Path(n))==h for n,h in users.items())
 assert sha(before_result)==before_hash
 assert {str(p.relative_to(partial)):sha(p) for p in partial.rglob('*') if p.is_file()}==partial_pins
preserved();old=Path(read(B/'full36/build/closure.json')['stage'])
for n,h in read(B/'full36/build/staging-manifest.json').items():
 assert sha(old/n)==h
 p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
for name in ['chapter_world_quality37.gd','chapter_world_quality37b.gd','chapter_world_quality37c.gd','chapter_masonry_quality37c.gdshader']:
 shutil.copy2(R/'chapter1/view'/name,S/'chapter1/view'/name)
observer=(H/'masonry37_compare.gd').read_text(encoding='utf-8')
observer=observer.replace(' var file=FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE);',''' var proxy_materials: Array=[]
 for node in view.world._solid_columns31:
  var mat: StandardMaterial3D=node.material_override
  proxy_materials.append({"name":String(node.name),"roughness":mat.roughness,"specular":mat.metallic_specular,"albedo":str(mat.albedo_color),"uv_scale":str(mat.uv1_scale),"shadow_mode":node.cast_shadow})
  assert(is_equal_approx(mat.roughness,.97) and is_equal_approx(mat.metallic_specular,.5) and mat.albedo_color==Color.WHITE)
 var file=FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE);''')
observer=observer.replace('"world":variant,','"world":variant,"proxy_materials":proxy_materials,')
observer=observer.replace('"Before31d vs isolated37, same earned normal arc9000 state. Three explicit rear inspection cameras and one original hero camera. Not normal camera walk/manual/performance."','"37c rear-only material; completed37b03 reference reused. Same earned Core36 arc9000 state and four camera targets. No costs measured; not manual/performance."')
(S/'compare37.gd').write_text(observer,encoding='utf-8');(O/'observer.gd').write_text(observer,encoding='utf-8')
pins={str(p.relative_to(S)):sha(p) for p in S.rglob('*') if p.is_file()}
(O/'SOURCE.json').write_text(json.dumps({'stage':str(S),'pins':pins,'reference':str(before_result),'reference_sha256':before_hash,'partial02_pins':partial_pins},indent=2),encoding='utf-8')
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
phases=[('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://compare37.gd']),('37c',['--script','res://compare37.gd','--resolution','1920x1080','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.arc','--chapter1-seed=90131','--masonry37-dir='+str(O/'37c'),'--masonry37-world=37c'])]
for label,args in phases:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  command=[engine,'--path',str(S)]+args;p=subprocess.Popen(command,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
  (O/(label+'-launch.json')).write_text(json.dumps({'pid':p.pid,'command':command}),encoding='utf-8');print(label,p.pid,flush=True)
  try:code=p.wait(timeout=180)
  except subprocess.TimeoutExpired:p.terminate();p.wait(timeout=30);raise
 result={'exit':code,'stderr_bytes':(O/(label+'.stderr.txt')).stat().st_size};(O/(label+'-execution.json')).write_text(json.dumps(result),encoding='utf-8');assert result=={'exit':0,'stderr_bytes':0},result
before=read(before_result);after=read(O/'37c/RESULT.json')
checks={'same_full_core':before['snapshot']==after['snapshot'],'same_all_anchors':before['anchors']==after['anchors'],'same_batches':before['batches']==after['batches'],'same_camera_records':before['records']==after['records'],'core_held':before['same_core_after_views'] and after['same_core_after_views'],'proxy_original_materials':len(after['proxy_materials'])==2}
assert all(checks.values());assert all(sha(S/n)==h for n,h in pins.items());preserved()
(O/'COMPARISON.json').write_text(json.dumps({'checks':checks,'visual_review_pending':True,'reference':str(before_result),'reference_sha256':before_hash,'scope':'37c material-only comparison against37b03 exact fullCore36+camera geometry. No timing measured. Product36/old evidence/user23/29/36 preserved.'},indent=2),encoding='utf-8');print('MASONRY37c COMPARE04 PASS; VISUAL REVIEW PENDING',flush=True)
