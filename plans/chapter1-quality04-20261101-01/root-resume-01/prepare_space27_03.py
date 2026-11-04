from pathlib import Path
import hashlib, json, shutil, subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent
O=B/'space27/compare03';S=Path('C:/Project/game-research/build-staging/chapter1-space27-compare03')
assert not O.exists() and not S.exists()
O.mkdir(parents=True);S.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
closure=read(B/'full26/build/closure.json')
print('closure keys',list(closure),flush=True)
old=Path(closure['stage'])
for n,h in read(B/'full26/build/staging-manifest.json').items():
 assert sha(old/n)==h
 p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
source=(R/'chapter1/view/chapter_ground_quality10.gdshader').read_text(encoding='utf-8')
start=source.index(' if(zone>1.5) {');end=source.index('\n ALBEDO=surface;',start)
source=source[:start]+''' float inlay_height=0.;
 if(zone>1.5) {
  // Authored stone rings are split into individual radial blocks. Narrow
  // recesses and bevels provide depth without adding collision or raised lips.
  float radius=length(p);
  float radial=abs(fract((radius-2.)/3.)-.5)*3.;
  float band=(1.-smoothstep(.18,.25,radial))*smoothstep(.6,.9,radius);
  float angle=atan(p.y,p.x);
  float ring_radius=max(1.5,floor((radius-2.)/3.)*3.+3.5);
  float divisions=max(12.,floor(ring_radius*2.1));
  float segment=fract((angle/6.2831853+.5)*divisions);
  float joint=1.-smoothstep(.015,.045,min(segment,1.-segment));
  float face=band*(1.-joint);
  float bevel=(1.-smoothstep(.15,.23,radial))*face;
  float variation=hash21(vec2(floor((radius-2.)/3.),floor((angle/6.2831853+.5)*divisions)));
  vec3 inlay=mix(stone*vec3(1.16,1.08,.88),vec3(.205,.187,.145),.45)*mix(.92,1.04,variation);
  inlay*=mix(.88,1.06,weather);
  surface*=vec3(.9,.91,1.04);
  surface=mix(surface,surface*.85,band*paving);
  surface=mix(surface,inlay,bevel*paving*.78);
  inlay_height=(bevel*.018-band*.006)*paving;
 }
''' + source[end:]
source=source.replace('float h=dot(stone,vec3(.3,.59,.11))*.12*paving;','float h=dot(stone,vec3(.3,.59,.11))*.12*paving+inlay_height;')
target=R/'chapter1/view/chapter_ground_quality27.gdshader';target.write_text(source,encoding='utf-8')
for name in ['chapter_ground_quality27.gdshader','chapter_world_quality27.gd']:
 shutil.copy2(R/'chapter1/view'/name,S/'chapter1/view'/name)
shutil.copy2(H/'space27_compare.gd',S/'compare.gd')
(S/'Compare.tscn').write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://compare.gd" id="1"]\n[node name="Compare" type="Node3D"]\nscript=ExtResource("1")\n',encoding='utf-8')
pins={str(p.relative_to(S)).replace('\\','/'):sha(p) for p in S.rglob('*') if p.is_file()}
(O/'source.json').write_text(json.dumps(dict(stage=str(S),pins=pins),indent=2))
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://compare.gd']),('gpu',['res://Compare.tscn','--resolution','1920x1080'])]:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  cmd=[engine,'--path',str(S)]+args;p=subprocess.Popen(cmd,stdout=out,stderr=err)
  (O/(label+'-launch.json')).write_text(json.dumps(dict(pid=p.pid,command=cmd),indent=2));print(label,p.pid,flush=True);code=p.wait(timeout=180)
 result=dict(exit=code,stderr_bytes=(O/(label+'.stderr.txt')).stat().st_size)
 (O/(label+'-execution.json')).write_text(json.dumps(result));assert result==dict(exit=0,stderr_bytes=0),result
shutil.copy2(S/'space27-result.json',O/'RESULT.json');shutil.copytree(S/'space27-shots',O/'shots')
assert all(sha(S/n)==h for n,h in pins.items())
assert all(sha(R/n)==h for n,h in read(B/'full26/FINAL-SOURCE-FREEZE.json').items())
print('PASS SPACE27 SOURCE STUDY; VISUAL REVIEW PENDING',flush=True)
