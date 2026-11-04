from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent
O=B/'actor28/fixture02';S=Path('C:/Project/game-research/build-staging/chapter1-actor28-fixture02')
assert not O.exists() and not S.exists();O.mkdir(parents=True);S.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=Path(read(B/'full27/build/closure.json')['stage'])
for n,h in read(B/'full27/build/staging-manifest.json').items():
 assert sha(old/n)==h
 p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
source=(R/'chapter1/view/chapter_actors_quality26.gd').read_text(encoding='utf-8').replace('26','28')
source=source.replace('var weight := .55*sin(PI*age)','var weight := .85*sin(PI*age)')
anchor=' # A modal or cold freeze holds the complete currently displayed pose.'
source=source.replace(anchor,''' # Recover retains the direction of the paid attack instead of stale travel.
 var facing_entity := _entity(actor)
 if playing and not dead and not facing_entity.is_empty() and facing_entity.state=="recover":
  direction=facing_entity.attack_direction
'''+anchor)
source=source.replace('  rig.set_bone_pose(index,original.interpolate_with(pose,weight))', '  var blended := original.interpolate_with(pose,weight)\n  if HIT28_BONES[i]=="Spine1":\n   var recoil_axis := (rig.get_bone_global_rest(index).basis.inverse()*Vector3.RIGHT).normalized()\n   blended.basis=blended.basis*Basis(recoil_axis,-.28*weight)\n  rig.set_bone_pose(index,blended)')
target=R/'chapter1/view/chapter_actors_quality28.gd';target.write_text(source,encoding='utf-8');shutil.copy2(target,S/'chapter1/view'/target.name)
fixture=(H/'hit26_fixture02.gd').read_text(encoding='utf-8').replace('26','28')
anchor='  e.state="move";run.tick+=20;actors.sync(run,.016)'
fixture=fixture.replace(anchor,'''  e.state="recover";e.direction=Vector2.UP;e.attack_direction=Vector2.RIGHT
  actor.rotation.y=0
  for sample in 12:actors.sync(run,.016)
  checks[role+"_recover_paid_facing"]=absf(angle_difference(actor.rotation.y,PI*.5))<.08
'''+anchor)
(S/'fixture.gd').write_text(fixture,encoding='utf-8')
(S/'Fixture.tscn').write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://fixture.gd" id="1"]\n[node name="Fixture" type="Node3D"]\nscript=ExtResource("1")\n',encoding='utf-8')
pins={str(p.relative_to(S)).replace('\\','/'):sha(p) for p in S.rglob('*') if p.is_file()}
(O/'source.json').write_text(json.dumps(dict(stage=str(S),pins=pins),indent=2),encoding='utf-8')
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('import',['--headless','--editor','--import']),('headless',['--headless','res://Fixture.tscn','--','--chapter1-profile-off','--chapter1-start','--chapter1-primary=chapter1.skill.ember','--chapter1-seed=90131'])]:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  cmd=[engine,'--path',str(S)]+args;p=subprocess.Popen(cmd,stdout=out,stderr=err);(O/(label+'-launch.json')).write_text(json.dumps(dict(pid=p.pid,command=cmd),indent=2));print(label,p.pid,flush=True);code=p.wait(timeout=180)
 result=dict(exit=code,stderr_bytes=(O/(label+'.stderr.txt')).stat().st_size);(O/(label+'-execution.json')).write_text(json.dumps(result));assert result==dict(exit=0,stderr_bytes=0),result
shutil.copy2(S/'hit28-fixture.json',O/'RESULT.json');assert all(sha(S/n)==h for n,h in pins.items());assert all(sha(R/n)==h for n,h in read(B/'full27/FINAL-SOURCE-FREEZE.json').items())
print('PASS ACTOR28 HEADLESS FIXTURE',flush=True)
