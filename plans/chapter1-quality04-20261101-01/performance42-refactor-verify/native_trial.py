"""Bounded isolated native trial; keeps every prior attempt and released file."""
from pathlib import Path
import json,shutil,subprocess,sys
from resume42 import pins,write,ENGINE,ROOT

here=Path(__file__).resolve().parent
action,label=sys.argv[1:]
assert label in ['overlap']
stage=Path('C:/Project/game-research/build-staging')/('diagnostic42-'+label+'-01')
proof=here/(label+'-native01')
if action=='prepare':
    assert not stage.exists() and not proof.exists()
    before=pins()
    shutil.copytree(Path('C:/Project/game-research/build-staging/diagnostic42-refactor-01'),stage,ignore=shutil.ignore_patterns('.godot'))
    trial=Path('C:/Project/game-research/build-staging')/('actor42-'+label+'-exact01')
    for name in ['chapter_actors_quality42.gd','chapter_actors_demon19.gd','chapter_actors_quality21.gd']:
        shutil.copy2(trial/'chapter1/view'/name,stage/'chapter1/view'/name)
    p=stage/'project.godot'
    p.write_text(p.read_text(encoding='utf-8-sig').replace('AshenCloisterDiagnostic42RefactorNative01','AshenCloisterDiagnostic42'+label.title()+'Native01'),encoding='utf-8')
    proof.mkdir()
    r=subprocess.run([str(ENGINE),'--headless','--path',str(stage),'--editor','--import','--quit'],capture_output=True,timeout=240)
    (proof/'import.stdout.bin').write_bytes(r.stdout);(proof/'import.stderr.bin').write_bytes(r.stderr)
    assert r.returncode==0 and b'ERROR:' not in r.stdout+r.stderr and before==pins()
    write(proof/'PRESERVATION-BEFORE.json',before)
    print('PREPARED',stage,flush=True)
elif action=='run':
    assert not (proof/'launch.json').exists()
    before=pins()
    cmd=[str(ENGINE),'--path',str(stage),'--script',str(ROOT/'artifacts/performance42-actors/observer42.gd'),'--windowed','--resolution','1920x1080','--rendering-method','forward_plus','--disable-vsync','--max-fps','0','--delta-smoothing','disable','--','--chapter1-profile-off','--chapter1-pilot','--chapter1-seed=90131','--chapter1-primary=chapter1.skill.frost','--performance42-dir='+str(proof/'raw')]
    with (proof/'stdout.txt').open('x',encoding='utf-8') as out,(proof/'stderr.txt').open('x',encoding='utf-8') as err:
        p=subprocess.Popen(cmd,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
        write(proof/'launch.json',{'pid':p.pid,'command':cmd});print('PID',p.pid,flush=True)
        code=p.wait(timeout=360)
    write(proof/'execution.json',{'exit':code,'preserved':before==pins()})
    assert code==0 and before==pins()
    print('EXIT',code,flush=True)
elif action=='analyze':
    source=(here.parent/'performance42-components/analyze42.py').read_text(encoding='utf-8')
    source=source.replace("H=Path(__file__).resolve().parent;R=H/'run04/raw'", "H=Path(__file__).resolve().parent/"+repr(proof.name)+";R=H/'raw'")
    assert not (proof/'ANALYSIS.json').exists()
    exec(compile(source,str(__file__),'exec'))
else:raise ValueError(action)
