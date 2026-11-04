from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'hit26/compare01';S=Path('C:/Project/game-research/build-staging/chapter1-hit26-replay01');read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not O.exists();O.mkdir();script=O/'hit26_compare.gd';shutil.copy2(H/script.name,script);pins=read(B/'hit26/replay01/source.json')['pins'];assert all(sha(S/n)==v for n,v in pins.items())
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('check',['--headless','--check-only']),('gpu',['--resolution','1920x1080','--fixed-fps','60'])]:
 cmd=[engine,'--path',str(S),'--script',str(script)]+args+['--','--chapter1-profile-off','--chapter1-start','--chapter1-primary=chapter1.skill.ember','--chapter1-seed=90131','--compare-output='+str(O/'shots')]
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  p=subprocess.Popen(cmd,stdout=out,stderr=err);(O/(label+'-launch.json')).write_text(json.dumps({'pid':p.pid,'command':cmd},indent=2));print(label,p.pid,flush=True);code=p.wait(timeout=120)
 report={'exit':code,'stderr_bytes':(O/(label+'.stderr.txt')).stat().st_size};(O/(label+'-execution.json')).write_text(json.dumps(report));assert code==0 and report['stderr_bytes']==0
shutil.copy2(O/'shots/RESULT.json',O/'RESULT.json');d=read(O/'RESULT.json');assert d['complete_original_core_restored'] and all(v['same_fixture_core'] for v in d['records']);assert all(sha(S/n)==v for n,v in pins.items());print('PASS HIT26 CLOSEUP',flush=True)
