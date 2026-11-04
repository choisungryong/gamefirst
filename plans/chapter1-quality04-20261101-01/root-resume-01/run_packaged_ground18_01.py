from pathlib import Path
import json,hashlib,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';HERE=Path(__file__).parent;OUT=B/'full18/runtime/ground-matrix01';assert not OUT.exists();OUT.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=read(B/'full18/build/build.json');exe=Path(build['exe']);assert sha(exe)==build['sha256']
# Preserve the source matrix runner, changing only where its output is written.
matrix=(HERE/'ground18_matrix.gd').read_text(encoding='utf-8')
matrix=matrix.replace('"res://ground18-result.json"',repr(str(OUT/'RESULT.json').replace('\\','/'))).replace('"res://ground18-shots"',repr(str(OUT/'shots').replace('\\','/'))).replace('"res://ground18-shots/"',repr(str(OUT/'shots').replace('\\','/')+'/'))
(OUT/'matrix.gd').write_text(matrix,encoding='utf-8')
bootstrap='extends SceneTree\nfunc _initialize() -> void:call_deferred("_boot")\nfunc _boot() -> void:\n\tvar script=load('+json.dumps(str(OUT/'matrix.gd').replace('\\','/'))+')\n\troot.add_child(script.new())\n'
(OUT/'bootstrap.gd').write_text(bootstrap,encoding='utf-8')
cmd=[str(exe),'--script',str(OUT/'bootstrap.gd'),'--','--chapter1-profile-off','--chapter1-start','--chapter1-qa-ignore-focus']
with (OUT/'stdout.txt').open('xb') as o,(OUT/'stderr.txt').open('xb') as e:
 p=subprocess.Popen(cmd,stdout=o,stderr=e);(OUT/'launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd,'exe_sha256':sha(exe),'matrix_sha256':sha(OUT/'matrix.gd'),'bootstrap_sha256':sha(OUT/'bootstrap.gd')},indent=2));print(p.pid,flush=True);code=p.wait(timeout=180)
report={'exit':code,'stderr_bytes':(OUT/'stderr.txt').stat().st_size};(OUT/'execution.json').write_text(json.dumps(report,indent=2));assert code==0 and report['stderr_bytes']==0,report
result=read(OUT/'RESULT.json');assert result['all_new_floor_covers'] and result['core_unchanged'] and len(result['cases'])==36
print(json.dumps({'cases':36,'old_failures':result['old_floor_fails'],'source_and_packaged_same_cases':result['cases']==read(B/'ground18/matrix01/RESULT.json')['cases']}),flush=True)
