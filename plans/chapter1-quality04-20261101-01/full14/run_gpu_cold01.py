from pathlib import Path
import json,sys,subprocess,hashlib,shutil,time
HERE=Path('C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/full14');ROOT=Path('C:/Project/d2r-combat-baseline')
mode="preview";run_id="gpu-cold01";assert mode in ['preview','native'] and run_id.replace('-','').isalnum()
build=json.loads((HERE/'build/build.json').read_text(encoding='utf-8'));exe=Path(build['exe'])
assert hashlib.sha256(exe.read_bytes()).hexdigest()==build['sha256']
proof=HERE/'runtime'/run_id;capture=exe.parent/'qa-captures'/run_id
assert not proof.exists() and not capture.exists();proof.mkdir(parents=True)
args=['--chapter1-profile-off','--chapter1-capture-dir='+str(capture)]
if mode=='preview':args+=['--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-quit-after=520','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131']
else:args+=['--chapter1-quit-after=150']
command=[str(exe),'--max-fps','120','--']+args
with (proof/'stdout.txt').open('x',encoding='utf-8') as stdout,(proof/'stderr.txt').open('x',encoding='utf-8') as stderr:
 process=subprocess.Popen(command,stdout=stdout,stderr=stderr,cwd=exe.parent)
 with (proof/'launch.json').open('x',encoding='utf-8') as f:json.dump({'pid':process.pid,'command':command,'mode':mode,'exe_sha256':build['sha256'],'profile_off':True,'scope':'Native input when mode=native; preview is normal QA driver on real GPU, not manual play or formal performance'},f,indent=2)
 print(json.dumps({'pid':process.pid,'proof':str(proof),'mode':mode}),flush=True)
 try:code=process.wait(timeout=570)
 except subprocess.TimeoutExpired:
  process.terminate();code=process.wait(timeout=15)
 if capture.exists():shutil.copytree(capture,proof/'captures')
 with (proof/'execution.json').open('x',encoding='utf-8') as f:json.dump({'actual_exit':code,'command':command,'stderr_bytes':(proof/'stderr.txt').stat().st_size,'capture_count':len(list(capture.glob('*.png'))) if capture.exists() else 0,'scope':'QA captures perturb frame times. Not formal performance, manual or heard-audio approval.'},f,indent=2)
 print(json.dumps({'actual_exit':code,'proof':str(proof)}),flush=True)
