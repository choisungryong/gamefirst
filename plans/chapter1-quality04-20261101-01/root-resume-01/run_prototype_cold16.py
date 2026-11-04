from pathlib import Path
import json,subprocess,hashlib
ROOT=Path('C:/Project/d2r-combat-baseline');OUT=ROOT/'plans/chapter1-quality04-20261101-01/cold16/prototype01';assert not OUT.exists();OUT.mkdir(parents=True)
exe=ROOT/'builds/chapter1/chapter1-full-candidate-20261101-14/AshenCloister-Chapter1.exe';script=Path(__file__).with_name('prototype_cold16.gd')
cmd=[str(exe),'--headless','--script',str(script)]
with(OUT/'stdout.txt').open('xb')as stdout,(OUT/'stderr.txt').open('xb')as stderr:
 p=subprocess.Popen(cmd,stdout=stdout,stderr=stderr);(OUT/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd},indent=2),encoding='utf-8');print(json.dumps({'pid':p.pid}),flush=True);code=p.wait(timeout=180)
r={'actual_exit':code,'stderr_bytes':(OUT/'stderr.txt').stat().st_size};(OUT/'execution.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r),flush=True)
assert code==0 and not r['stderr_bytes'],r
