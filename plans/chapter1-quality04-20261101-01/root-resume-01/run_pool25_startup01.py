from pathlib import Path
import json,subprocess,shutil,hashlib
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'pool25/startup01';S=Path('C:/Project/game-research/build-staging/chapter1-pool25-warm-replay01')
assert not O.exists();O.mkdir(parents=True)
script=O/'pool25_startup.gd';shutil.copy2(H/script.name,script)
cmd=['C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe','--path',str(S),'--headless','--script',str(script),'--','--startup-output='+str(O/'RESULT.json')]
with (O/'stdout.txt').open('xb') as out,(O/'stderr.txt').open('xb') as err:
 p=subprocess.Popen(cmd,stdout=out,stderr=err);(O/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd},indent=2));code=p.wait(timeout=120)
(O/'execution.json').write_text(json.dumps({'exit':code,'stderr_bytes':(O/'stderr.txt').stat().st_size}));assert code==0 and (O/'stderr.txt').stat().st_size==0
print((O/'RESULT.json').read_text())
