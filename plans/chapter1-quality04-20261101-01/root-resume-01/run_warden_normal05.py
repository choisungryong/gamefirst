from pathlib import Path
import subprocess,json,shutil,hashlib,time
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01/boss-research12'
STAGE=Path('C:/Project/game-research/build-staging/chapter1-warden-clock-20261101-04')
OUT=BASE/'normal05';assert not OUT.exists();OUT.mkdir()
capture=STAGE/'plans/chapter1-quality04-20261101-01/boss-research12/normal05/captures';assert not capture.exists()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
frozen=json.loads((ROOT/'plans/chapter1-quality04-20261101-01/full11/FINAL-SOURCE-FREEZE.json').read_text(encoding='utf-8'))
assert all(sha(ROOT/n)==h for n,h in frozen.items())
with(OUT/'runtime-source.json').open('x',encoding='utf-8')as f:json.dump({'stage':str(STAGE),'chapter11_root_freeze_matches':True,'sha256':{str(p.relative_to(STAGE)).replace('\\','/'):sha(p)for p in STAGE.rglob('*')if p.is_file()and'.godot'not in p.parts and p.suffix in ['.gd','.gdshader','.glb','.tscn','.godot']and'plans'not in p.parts},'scope':'Source/debug actual GPU normal policy. Not release/manual/audio/performance approval.'},f,indent=2)
cmd=['C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe','--path',str(STAGE),'--max-fps','120','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-seed=90131','--chapter1-capture-dir='+str(capture),'--chapter1-quit-after=520']
start=time.time()
with(OUT/'stdout.txt').open('xb')as stdout,(OUT/'stderr.txt').open('xb')as stderr:
 p=subprocess.Popen(cmd,stdout=stdout,stderr=stderr)
 with(OUT/'launch.json').open('x',encoding='utf-8')as f:json.dump({'pid':p.pid,'command':cmd,'scope':'Source/debug actual GPU, normal input policy, profile off'},f,indent=2)
 print(json.dumps({'pid':p.pid,'proof':str(OUT)}),flush=True)
 try:code=p.wait(timeout=580)
 except subprocess.TimeoutExpired:p.kill();p.wait();raise
if capture.exists():shutil.copytree(capture,OUT/'captures')
with(OUT/'execution.json').open('x',encoding='utf-8')as f:json.dump({'actual_exit':code,'stderr_bytes':(OUT/'stderr.txt').stat().st_size,'wall_seconds':time.time()-start,'capture_count':len(list((OUT/'captures').glob('*.png'))) if (OUT/'captures').exists() else 0,'scope':'Source/debug GPU normal driver, not final release/manual/audio/performance'},f,indent=2)
print(json.dumps({'actual_exit':code,'stderr_bytes':(OUT/'stderr.txt').stat().st_size}),flush=True)
