from pathlib import Path
import json,subprocess,shutil
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'elements15/caps01';STAGE=Path('C:/Project/game-research/build-staging/chapter1-elements15-normal-20261101-01')
assert (BASE/'elements15/normal01/gpu-execution.json').exists(),'Observe the live normal15 run first; do not overlap its user log'
assert not OUT.exists();OUT.mkdir();script=OUT/'caps.gd';shutil.copy2(Path(__file__).with_name('elements_caps15.gd'),script)
runner=OUT/'runner.gd';runner.write_text('extends SceneTree\nfunc _initialize() -> void:call_deferred("execute")\nfunc execute() -> void:\n\troot.add_child(load("'+script.as_posix()+'").new())\n',encoding='utf-8')
cmd=['C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe','--headless','--path',str(STAGE),'--script',str(runner),'--','--chapter1-profile-off','--chapter1-start','--chapter1-qa-ignore-focus']
with(OUT/'stdout.txt').open('xb')as stdout,(OUT/'stderr.txt').open('xb')as stderr:
 p=subprocess.Popen(cmd,stdout=stdout,stderr=stderr);(OUT/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd},indent=2),encoding='utf-8');print(json.dumps({'pid':p.pid}),flush=True);code=p.wait(timeout=60)
r={'actual_exit':code,'stderr_bytes':(OUT/'stderr.txt').stat().st_size};(OUT/'execution.json').write_text(json.dumps(r,indent=2),encoding='utf-8');assert code==0 and not r['stderr_bytes'],r
result=json.loads((OUT/'result.json').read_text(encoding='utf-8'));assert not result['failures'];print(json.dumps(result),flush=True)
