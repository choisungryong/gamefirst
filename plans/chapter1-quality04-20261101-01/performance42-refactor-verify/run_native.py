from pathlib import Path
import subprocess,json
from resume42 import pins,write,ENGINE,ROOT

proof=Path(__file__).resolve().parent/'native01'
assert not (proof/'launch.json').exists()
before=pins()
cmd=[str(ENGINE),'--path','C:/Project/game-research/build-staging/diagnostic42-refactor-01','--script',str(ROOT/'artifacts/performance42-actors/observer42.gd'),'--windowed','--resolution','1920x1080','--rendering-method','forward_plus','--disable-vsync','--max-fps','0','--delta-smoothing','disable','--','--chapter1-profile-off','--chapter1-pilot','--chapter1-seed=90131','--chapter1-primary=chapter1.skill.frost','--performance42-dir='+str(proof/'raw')]
with (proof/'stdout.txt').open('x',encoding='utf-8') as out,(proof/'stderr.txt').open('x',encoding='utf-8') as err:
    process=subprocess.Popen(cmd,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
    write(proof/'launch.json',{'pid':process.pid,'command':cmd})
    print('PID',process.pid,flush=True)
    code=process.wait(timeout=360)
write(proof/'execution.json',{'exit':code,'preserved':pins()==before})
assert pins()==before and code==0
print('EXIT',code,flush=True)
