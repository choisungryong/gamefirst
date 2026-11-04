"""CPU/headless-only verification; preserve stdout/stderr and exact commands."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path('C:/Project/d2r-combat-baseline')
HERE=Path(__file__).resolve().parent
ENGINE=Path('C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe')
out=HERE/'contract-test-02'
assert not out.exists();out.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    assert not p.exists()
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
commands=[('pure',[str(ENGINE),'--headless','--path',str(ROOT),'--script','plans/chapter1-quality04-20261101-01/measurement/test_frame_probe.gd']),
          ('scene-parse',[str(ENGINE),'--headless','--path',str(ROOT),'--check-only','--script','chapter1/chapter_view.gd'])]
results={}
for label,command in commands:
    result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=45)
    record={'command':command,'actual_exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'scope':'CPU/headless parse or injected-clock tests; no performance observation'}
    write(out/(label+'-execution.json'),record)
    results[label]=result.returncode==0 and not any(s in result.stdout+result.stderr for s in ('SCRIPT ERROR','ERROR:','WARNING:'))
    if label=='pure':
        marker='FRAME_PROBE_PURE_TEST '
        tests=[json.loads(s.split(marker,1)[1]) for s in result.stdout.splitlines() if marker in s]
        results['pure_result']=len(tests)==1 and tests[0]['checks']>=21 and not tests[0]['failures']
for rel in ('measurement/run_probe.py','measurement/verify_contract.py','packaging/package_quality04.py'):
    p=HERE.parent/rel
    compile(p.read_text(encoding='utf-8'),str(p),'exec')
    results['syntax_'+rel]=True
pins={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'chapter1/presentation/frame_probe.gd',ROOT/'chapter1/chapter_view.gd',HERE/'test_frame_probe.gd',HERE/'run_probe.py',HERE.parent/'packaging/package_quality04.py')}
write(out/'result.json',{'success':all(results.values()),'checks':results,'source_pins_at_test':pins,'formal_gpu_runs':0,'exports':0})
print(json.dumps({'success':all(results.values()),'checks':results,'evidence':str(out)}))
sys.exit(0 if all(results.values()) else 1)
