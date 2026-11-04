"""Launch ordinary menu for parent-controlled UI QA, retaining real process exit."""
from pathlib import Path
import json
import subprocess
import time

PROOF=Path(__file__).resolve().parent
EXE=Path('C:/Project/d2r-combat-baseline/builds/chapter1/chapter1-c2-candidate-20261031-01/AshenCloister-Chapter1.exe')
DEST=EXE.parent/'qa-captures/root-native01'
assert not DEST.exists()
assert not (PROOF/'native-menu-launch.json').exists()
DEST.mkdir(parents=True)
command=[str(EXE),'--log-file',str(DEST/'godot.log'),'--','--chapter1-capture-dir='+str(DEST)]
started=time.time()
with (DEST/'stdout.log').open('wb') as out, (DEST/'stderr.log').open('wb') as err:
    process=subprocess.Popen(command,stdout=out,stderr=err)
    record={'pid':process.pid,'command':command,'scope':'Ordinary menu; parent is sole native UI controller. No start/pilot/focus-skip flags.'}
    (PROOF/'native-menu-launch.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(record),flush=True)
    code=process.wait()
record.update({'actual_exit':code,'elapsed_wall_seconds':time.time()-started})
(PROOF/'native-menu-exit.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'actual_exit':code}),flush=True)
raise SystemExit(code)
