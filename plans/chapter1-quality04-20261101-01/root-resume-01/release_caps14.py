from pathlib import Path
import json,subprocess
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'full14/release-caps01';assert not OUT.exists();OUT.mkdir()
s=Path(__file__).with_name('elements_caps14.gd').read_text(encoding='utf-8').replace('res://caps-result.json',(OUT/'result.json').as_posix())
script=OUT/'caps.gd';script.write_text(s,encoding='utf-8')
runner=OUT/'runner.gd';runner.write_text('extends SceneTree\nfunc _initialize() -> void:call_deferred("execute")\nfunc execute() -> void:\n\tvar script=load("'+script.as_posix()+'")\n\troot.add_child(script.new())\n',encoding='utf-8')
exe=ROOT/'builds/chapter1/chapter1-full-candidate-20261101-14/AshenCloister-Chapter1.exe'
cmd=[str(exe),'--headless','--verbose','--script',str(runner),'--','--chapter1-profile-off','--chapter1-start','--chapter1-qa-ignore-focus']
with(OUT/'stdout.txt').open('xb')as stdout,(OUT/'stderr.txt').open('xb')as stderr:
 p=subprocess.Popen(cmd,stdout=stdout,stderr=stderr);(OUT/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd},indent=2),encoding='utf-8');print(json.dumps({'pid':p.pid}),flush=True);code=p.wait(timeout=90)
r={'actual_exit':code,'stderr_bytes':(OUT/'stderr.txt').stat().st_size};(OUT/'execution.json').write_text(json.dumps(r,indent=2),encoding='utf-8');assert code==0 and not r['stderr_bytes'],r
result=json.loads((OUT/'result.json').read_text(encoding='utf-8'));assert not result['failures'];print(json.dumps(result),flush=True)
