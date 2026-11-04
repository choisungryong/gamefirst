from pathlib import Path
import subprocess,json,hashlib
R=Path(__file__).resolve().parent
ENGINE='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
ROOT='C:/Project/d2r-combat-baseline'
base=[ENGINE,'--headless','--path',ROOT]
jobs=[('fixture-positive',base+['--script','res://plans/chapter1-quality-20261031-01/fx/test_presentation.gd']),('fixture-negative',base+['--script','res://plans/chapter1-quality-20261031-01/fx/test_presentation.gd','--','--prove-failure']),('scene-smoke',base+['res://chapter1/Chapter1.tscn','--','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-quit-after=2'])]
summary=[]
for name,argv in jobs:
    target=R/(name+'-execution.json');assert not target.exists()
    p=subprocess.run(argv,capture_output=True,text=True,timeout=60)
    data={'argv':argv,'actual_exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    summary.append({'name':name,'actual_exit':p.returncode,'script_error':'SCRIPT ERROR' in p.stdout+p.stderr,'engine_error':'ERROR:' in p.stdout+p.stderr})
print(json.dumps(summary))
