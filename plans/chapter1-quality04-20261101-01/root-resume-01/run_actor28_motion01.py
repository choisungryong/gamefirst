from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'actor28/motion01';assert not O.exists();O.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=read(B/'actor28/fixture01/source.json');S=Path(source['stage']);assert all(sha(S/n)==h for n,h in source['pins'].items());script=O/'actor28_motion.gd';shutil.copy2(H/script.name,script)
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('check',['--headless','--check-only']),('gpu',['--resolution','1280x720','--fixed-fps','60'])]:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  cmd=[engine,'--path',str(S),'--script',str(script)]+args+['--','--chapter1-profile-off','--chapter1-start','--chapter1-primary=chapter1.skill.ember','--chapter1-seed=90131','--motion-output='+str(O/'shots')];p=subprocess.Popen(cmd,stdout=out,stderr=err);(O/(label+'-launch.json')).write_text(json.dumps(dict(pid=p.pid,command=cmd),indent=2));print(label,p.pid,flush=True);code=p.wait(timeout=180)
 result=dict(exit=code,stderr_bytes=(O/(label+'.stderr.txt')).stat().st_size);(O/(label+'-execution.json')).write_text(json.dumps(result));assert result==dict(exit=0,stderr_bytes=0),result
shutil.copy2(O/'shots/RESULT.json',O/'RESULT.json');d=read(O/'RESULT.json');assert d['complete_original_core_restored'] and all(v['same_fixture_core'] for v in d['records']);assert all(sha(S/n)==h for n,h in source['pins'].items());print('PASS ACTOR28 MOTION SAMPLES; VISUAL REVIEW PENDING',flush=True)
