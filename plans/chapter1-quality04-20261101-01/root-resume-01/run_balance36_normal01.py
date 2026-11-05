from pathlib import Path
import json,hashlib,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'balance36/normal01';assert not O.exists();O.mkdir()
a=json.loads((B/'balance36/rules02/SOURCE.json').read_text());S=Path(a['stage']);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert all(sha(S/n)==h for n,h in a['pins'].items())
script=H/'balance36_normal.gd';(O/'SOURCE.json').write_text(json.dumps({'reused_stage':str(S),'source':str(B/'balance36/rules02/SOURCE.json'),'observer_sha256':sha(script)},indent=2))
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('check',['--headless','--check-only','--script',str(script)]),('normal',['--headless','--script',str(script)])]:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  cmd=[engine,'--path',str(S)]+args;p=subprocess.Popen(cmd,stdout=out,stderr=err);(O/(label+'-launch.json')).write_text(json.dumps({'pid':p.pid,'command':cmd}));print(label,p.pid,flush=True);code=p.wait(timeout=300)
 result={'exit':code,'stderr_bytes':(O/(label+'.stderr.txt')).stat().st_size};(O/(label+'-execution.json')).write_text(json.dumps(result));print(label,result,flush=True);assert result=={'exit':0,'stderr_bytes':0},result
print('NORMAL36 PASS; REVIEW PACING AND BALANCE',flush=True)
