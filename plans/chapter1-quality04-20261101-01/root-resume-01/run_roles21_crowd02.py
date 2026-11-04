from pathlib import Path
import json,hashlib,shutil,subprocess,struct
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'roles21/crowd02';assert not O.exists();O.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe';results={}
results={'candidate20':read(B/'roles21/crowd01/candidate20-result.json')}
for variant in ['roles21']:
 S=Path('C:/Project/game-research/build-staging/chapter1-roles21-crowd02-'+variant);assert not S.exists();S.mkdir()
 old=Path(read(B/'full20/build/closure.json')['stage']);pins=read(B/'full20/build/staging-manifest.json')
 for n,h in pins.items():
  assert sha(old/n)==h
  p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
 if variant=='roles21':
  n='chapter1/view/chapter_actors_quality21.gd';shutil.copy2(R/n,S/n)
  p=S/'chapter1/chapter_one_view.gd';p.write_text(p.read_text(encoding='utf-8').replace('chapter_actors_quality20.gd','chapter_actors_quality21.gd'),encoding='utf-8')
 shutil.copy2(H/'roles21_crowd.gd',S/'crowd.gd')
 (S/'Crowd.tscn').write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://crowd.gd" id="1"]\n[node name="Crowd" type="Node3D"]\nscript=ExtResource("1")\n',encoding='utf-8')
 frozen={str(p.relative_to(S)).replace('\\','/'):sha(p) for p in S.rglob('*') if p.is_file()};write(O/(variant+'-source.json'),{'stage':str(S),'pins':frozen})
 for label,args in [('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://crowd.gd']),('gpu',['res://Crowd.tscn','--','--chapter1-profile-off','--chapter1-start','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131'])]:
  prefix=variant+'-'+label
  with (O/(prefix+'.stdout.txt')).open('xb') as out,(O/(prefix+'.stderr.txt')).open('xb') as err:
   cmd=[engine,'--path',str(S)]+args;p=subprocess.Popen(cmd,stdout=out,stderr=err);write(O/(prefix+'-launch.json'),{'pid':p.pid,'command':cmd});print(prefix,p.pid,flush=True);code=p.wait(timeout=240)
  report={'exit':code,'stderr_bytes':(O/(prefix+'.stderr.txt')).stat().st_size};write(O/(prefix+'-execution.json'),report);assert code==0 and report['stderr_bytes']==0,report
 for name in ['result','samples']:shutil.copy2(S/('crowd21-'+name+'.json'),O/(variant+'-'+name+'.json'))
 shutil.copy2(S/'crowd21.png',O/(variant+'.png'));assert struct.unpack_from('>II',(S/'crowd21.png').read_bytes(),16)==(1920,1080)
 results[variant]=read(S/'crowd21-result.json');assert results[variant]['core_restored'];assert all(sha(S/n)==h for n,h in frozen.items())
freeze=read(B/'full20/FINAL-SOURCE-FREEZE.json');assert all(sha(R/n)==h for n,h in freeze.items())
write(O/'RESULT.json',{'results':results,'root20_preserved':True});print('PASS',flush=True)
