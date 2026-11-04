from pathlib import Path
import json,subprocess,time
ROOT=Path('C:/Project/d2r-combat-baseline')
PROOF=ROOT/'plans/chapter1-c2-20261031-01/package-candidate02'
EXE=ROOT/'builds/chapter1/chapter1-c2-candidate-20261031-02/AshenCloister-Chapter1.exe'
DEST=EXE.parent/'qa-captures/root-native02'
assert EXE.is_file() and not DEST.exists()
assert not (PROOF/'native-menu-launch.json').exists()
DEST.mkdir(parents=True)
command=[str(EXE),'--log-file',str(DEST/'godot.log'),'--','--chapter1-capture-dir='+str(DEST)]
started=time.time()
with (DEST/'stdout.log').open('wb') as out,(DEST/'stderr.log').open('wb') as err:
    p=subprocess.Popen(command,stdout=out,stderr=err)
    record={'pid':p.pid,'command':command,'scope':'Ordinary menu; parent sole native UI controller; no autostart/pilot/focus-skip/input-log flags.'}
    (PROOF/'native-menu-launch.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(record),flush=True)
    code=p.wait()
record.update({'actual_exit':code,'elapsed_wall_seconds':time.time()-started})
(PROOF/'native-menu-exit.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'actual_exit':code}),flush=True)
raise SystemExit(code)
