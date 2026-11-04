from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent
O=B/'motion19/fixture01';S=Path('C:/Project/game-research/build-staging/chapter1-motion19-fixture01')
assert not O.exists() and not S.exists();O.mkdir(parents=True);S.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=read(B/'motion19/release01/source.json');old=Path(source['stage'])
for n,h in source['pins'].items():
 assert sha(old/n)==h
 p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
shutil.copy2(H/'motion19_fixture.gd',S/'fixture.gd')
(S/'Fixture.tscn').write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://fixture.gd" id="1"]\n[node name="Fixture" type="Node3D"]\nscript=ExtResource("1")\n',encoding='utf-8')
pins={str(p.relative_to(S)).replace('\\','/'):sha(p) for p in S.rglob('*') if p.is_file()}
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
write(O/'source.json',{'stage':str(S),'pins':pins})
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://fixture.gd']),('gpu',['res://Fixture.tscn','--fixed-fps','60','--','--chapter1-profile-off','--chapter1-start','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131'])]:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  cmd=[engine,'--path',str(S)]+args;p=subprocess.Popen(cmd,stdout=out,stderr=err);write(O/(label+'-launch.json'),{'pid':p.pid,'command':cmd});print(label,p.pid,flush=True);code=p.wait(timeout=120)
 report={'exit':code,'stderr_bytes':(O/(label+'.stderr.txt')).stat().st_size};write(O/(label+'-execution.json'),report);assert code==0 and report['stderr_bytes']==0,report
shutil.copy2(S/'fixture-result.json',O/'RESULT.json');shutil.copytree(S/'fixture-shots',O/'shots')
assert all(sha(S/n)==h for n,h in pins.items())
freeze=read(B/'full18/FINAL-SOURCE-FREEZE.json');assert all(sha(R/n)==h for n,h in freeze.items())
print('PASS',flush=True)
