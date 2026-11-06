import hashlib,json,pathlib,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parent
PROJECT=pathlib.Path(r'C:\Project\d2r-combat-baseline')
EXE=PROJECT/'builds/chapter1/chapter1-full-candidate-20261106-36/AshenCloister-Chapter1.exe'
PINS=PROJECT/'plans/chapter1-quality04-20261101-01/full36/USER-PRESERVATION-ADDENDUM02.json'
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def pins():return {p:sha(p)==h for p,h in json.loads(PINS.read_text(encoding='utf-8-sig'))['user_pins'].items()}
before=pins();assert all(before.values())
results=[]
for mode in ('model_live','model_cleanup'):
    folder=ROOT/mode;folder.mkdir(exist_ok=False)
    command=[str(EXE),'--headless','--verbose','--fixed-fps','60','--script',str(ROOT/'model_terminal_probe.gd'),'--','--chapter1-profile-off',f'--exit-mode={mode}',f'--exit-dir={folder}']
    (folder/'launch.json').write_text(json.dumps({'command':command,'exe_sha256':sha(EXE),'observer_sha256':sha(ROOT/'model_terminal_probe.gd')},indent=2),encoding='utf-8')
    started=time.monotonic()
    with (folder/'stdout.txt').open('wb') as out,(folder/'stderr.txt').open('wb') as err:proc=subprocess.run(command,stdout=out,stderr=err,timeout=120)
    entry={'mode':mode,'exit_code':proc.returncode,'elapsed_seconds':round(time.monotonic()-started,3),'stderr_bytes':(folder/'stderr.txt').stat().st_size,'leak_warning':'ObjectDB instances leaked' in (folder/'stderr.txt').read_text(errors='replace')}
    (folder/'execution.json').write_text(json.dumps(entry,indent=2),encoding='utf-8');results.append(entry)
after=pins()
(ROOT/'MODEL-SUMMARY.json').write_text(json.dumps({'cases':results,'user_pins_before':before,'user_pins_after':after,'exe_sha256':sha(EXE),'scope':'Core-only terminal lifecycle; original acquisition NOT rerun; no saved rewards.'},indent=2),encoding='utf-8')
print(json.dumps({'cases':results,'preservation':all(after.values())},indent=2))
