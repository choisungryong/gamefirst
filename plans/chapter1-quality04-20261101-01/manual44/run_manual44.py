from pathlib import Path
import importlib.util,json,shutil,subprocess

here=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('final44',here.parent/'final-performance44/run_performance44.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
proof=here/'attempt01';assert not proof.exists()
before=m.package_snapshot()
running=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object {$_.Name -like 'Godot*' -or $_.Name -like 'AshenCloister*'} | Select-Object -ExpandProperty ProcessId"],capture_output=True,text=True,check=True)
assert not running.stdout.strip(),'Do not compete with an existing game'
proof.mkdir();m.write(proof/'PRESERVATION-BEFORE.json',before)
observer=here/'manual44_observer.gd';shutil.copy2(observer,proof/observer.name)
checked=subprocess.run([str(m.EXE),'--headless','--check-only','--script',str(observer)],capture_output=True,timeout=45)
(proof/'check.stdout.bin').write_bytes(checked.stdout);(proof/'check.stderr.bin').write_bytes(checked.stderr)
m.write(proof/'CHECK.json',{'exit':checked.returncode,'stderr_bytes':len(checked.stderr),'observer_sha256':m.sha(observer)})
assert checked.returncode==0 and not checked.stderr
capture=m.EXE.parent/'qa-captures/manual-20261113-01';assert not capture.exists()
cmd=[str(m.EXE),'--script',str(observer),'--windowed','--resolution','1600x900','--rendering-method','forward_plus','--max-fps','120','--','--chapter1-profile-off','--chapter1-seed=90131','--chapter1-capture-dir='+str(capture),'--chapter1-quit-after=1700']
with (proof/'stdout.bin').open('xb') as out,(proof/'stderr.bin').open('xb') as err:
    p=subprocess.Popen(cmd,cwd=m.EXE.parent,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
    m.write(proof/'launch.json',{'pid':p.pid,'command':cmd,'exe_sha256':m.sha(m.EXE),'observer_sha256':m.sha(observer),'native_inputs_only':True})
    print('MANUAL44_PID',p.pid,flush=True)
    timed_out=False
    try:code=p.wait(timeout=1800)
    except subprocess.TimeoutExpired:
        timed_out=True;p.terminate();code=p.wait(timeout=10)
raw=(proof/'stdout.bin').read_bytes()
try:text=raw.decode('utf-8')
except UnicodeDecodeError:text=raw.decode('cp949',errors='replace')
(proof/'stdout.txt').write_text(text,encoding='utf-8')
final=[json.loads(line.split('MANUAL44_FINAL ',1)[1]) for line in text.splitlines() if 'MANUAL44_FINAL ' in line]
after=m.package_snapshot()
m.write(proof/'execution.json',{'actual_exit':code,'timeout':timed_out,'stderr_bytes':(proof/'stderr.bin').stat().st_size,'preserved':before==after})
if capture.exists():shutil.copytree(capture,proof/'captures')
if final:
    result=final[-1];result['manual_victory_observed']=result['snapshot']['mode']=='victory'
    m.write(proof/'RESULT.json',result)
    print(json.dumps({'manual_victory_observed':result['manual_victory_observed'],'mode':result['snapshot']['mode']}),flush=True)
assert before==after and code==0 and not timed_out and (proof/'stderr.bin').stat().st_size==0
