"""Single actual36 profile-OFF full-scene lifecycle; fresh evidence only."""
import hashlib,json,pathlib,subprocess,time
HERE=pathlib.Path(__file__).resolve().parent
PROJECT=pathlib.Path('C:/Project/d2r-combat-baseline')
EXE=PROJECT/'builds/chapter1/chapter1-full-candidate-20261106-36/AshenCloister-Chapter1.exe'
PINFILE=HERE.parent.parent/'USER-PRESERVATION-ADDENDUM02.json'
EXPECTED='a889be6fcb57120083d78e84dacd4ae4976482edb04285ef017dbf37e993e22f'
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def pins():return {p:sha(p)==h for p,h in json.loads(PINFILE.read_text(encoding='utf-8-sig'))['user_pins'].items()}
def write(p,v):
    with pathlib.Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,indent=2);f.write('\n')
assert sha(EXE)==EXPECTED
before=pins();assert all(before.values())
FOLDER=HERE/'actual';FOLDER.mkdir(exist_ok=False)
command=[str(EXE),'--headless','--verbose','--fixed-fps','60','--script',str(HERE/'scene_exit_probe.gd'),'--',
         '--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus',
         '--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131',f'--scene-exit-dir={FOLDER}']
write(FOLDER/'launch.json',{'command':command,'exe_sha256':sha(EXE),'observer_sha256':sha(HERE/'scene_exit_probe.gd'),'user_pins_before':before,'timeout_seconds':180})
started=time.monotonic();timed_out=False
with (FOLDER/'stdout.txt').open('xb') as out,(FOLDER/'stderr.txt').open('xb') as err:
    try:
        p=subprocess.run(command,stdout=out,stderr=err,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
        exit_code=p.returncode
    except subprocess.TimeoutExpired:
        timed_out=True;exit_code=None
after=pins();stderr=(FOLDER/'stderr.txt').read_text(errors='replace');stdout=(FOLDER/'stdout.txt').read_text(errors='replace')
result=json.loads((FOLDER/'RESULT.json').read_text()) if (FOLDER/'RESULT.json').exists() else None
execution={'actual_exit':exit_code,'timeout':timed_out,'wall_seconds':round(time.monotonic()-started,3),
           'stderr_bytes':(FOLDER/'stderr.txt').stat().st_size,'leak_warning':'ObjectDB instances leaked' in stderr+stdout,
           'user_pins_after':after,'exe_unchanged':sha(EXE)==EXPECTED,'terminal_result':result,
           'passed':exit_code==0 and not timed_out and not stderr and 'ERROR:' not in stdout and result is not None and result['terminal_predicate_pass'] and all(after.values()) and sha(EXE)==EXPECTED}
write(FOLDER/'execution.json',execution)
print(json.dumps(execution,indent=2))
