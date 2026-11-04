from pathlib import Path
import json,hashlib,subprocess,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'full23/performance/render-preflight01';assert not O.exists();O.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=read(B/'full23/build/build.json');exe=Path(build['exe']);assert sha(exe)==build['sha256'];capture=exe.parent/'qa-captures/render23-preflight01';assert not capture.exists()
cmd=[str(exe),'--script',str(H/'render23_preflight.gd'),'--windowed','--resolution','1920x1080','--rendering-method','forward_plus','--disable-vsync','--max-fps','0','--','--chapter1-profile-off']
with (O/'stdout.txt').open('xb') as out,(O/'stderr.txt').open('xb') as err:
 p=subprocess.Popen(cmd,cwd=exe.parent,stdout=out,stderr=err);(O/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd,'exe_sha256':sha(exe),'observer_sha256':sha(H/'render23_preflight.gd')},indent=2),encoding='utf-8');print('render23-preflight',p.pid,flush=True);code=p.wait(timeout=45)
(O/'execution.json').write_text(json.dumps({'exit':code,'stderr_bytes':(O/'stderr.txt').stat().st_size}),encoding='utf-8');assert code==0 and (O/'stderr.txt').stat().st_size==0
rows=[json.loads(s.split('RENDER23_PREFLIGHT ',1)[1]) for s in (O/'stdout.txt').read_text(encoding='utf-8').splitlines() if 'RENDER23_PREFLIGHT ' in s];assert len(rows)==1
(O/'RESULT.json').write_text(json.dumps(rows[0],ensure_ascii=False,indent=2),encoding='utf-8');shutil.copytree(capture,O/'captures');assert sha(exe)==build['sha256'];print(rows[0],flush=True)
