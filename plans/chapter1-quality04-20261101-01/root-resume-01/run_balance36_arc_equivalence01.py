from pathlib import Path
import json,subprocess,hashlib
H=Path(__file__).parent;B=H.parent;O=B/'balance36/arc-segments01/equivalence01';S=Path('C:/Project/game-research/build-staging/chapter1-balance36-arc02');script=H/'balance36_arc_equivalence.gd'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins=json.loads((B/'balance36/arc02/SOURCE.json').read_text())['pins'];assert all(sha(S/n)==h for n,h in pins.items())
(O/'SOURCE.json').write_text(json.dumps({'stage':str(S),'inherited_pins':str(B/'balance36/arc02/SOURCE.json'),'script_sha256':sha(script)},indent=2))
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('check',['--headless','--check-only','--script',str(script)]),('equivalence',['--headless','--script',str(script)])]:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  cmd=[engine,'--path',str(S)]+args;p=subprocess.Popen(cmd,stdout=out,stderr=err);(O/(label+'-launch.json')).write_text(json.dumps({'pid':p.pid,'command':cmd}));code=p.wait(timeout=240)
 result={'exit':code,'stderr_bytes':(O/(label+'.stderr.txt')).stat().st_size};(O/(label+'-execution.json')).write_text(json.dumps(result));print(label,result,flush=True);assert result=={'exit':0,'stderr_bytes':0},result
