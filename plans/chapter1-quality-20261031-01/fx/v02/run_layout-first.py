from pathlib import Path
import subprocess,json
HERE=Path(__file__).resolve().parent
ENGINE='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
ROOT='C:/Project/d2r-combat-baseline'
base=[ENGINE,'--headless','--path',ROOT,'--script','res://plans/chapter1-quality-20261031-01/fx/v02/test_layout.gd']
for name,extra in [('layout-current',[]),('layout-intentional',['--prove-failure']),('layout-before',['--hud-before'])]:
    target=HERE/(name+'-execution.json')
    assert not target.exists(),target
    argv=base+(['--']+extra if extra else [])
    p=subprocess.run(argv,capture_output=True,encoding='utf-8',errors='replace',timeout=60)
    target.write_text(json.dumps({'argv':argv,'actual_exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(name,p.returncode,p.stdout,p.stderr)
