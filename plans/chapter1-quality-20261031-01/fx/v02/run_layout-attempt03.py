from pathlib import Path
import subprocess,json
HERE=Path(__file__).resolve().parent
OUTPUT=HERE/'attempt03-raw'
OUTPUT.mkdir(exist_ok=False)
ENGINE='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
ROOT='C:/Project/d2r-combat-baseline'
base=[ENGINE,'--headless','--path',ROOT,'--script','res://plans/chapter1-quality-20261031-01/fx/v02/test_layout.gd']
for name,extra in [('layout-current',[]),('layout-intentional',['--prove-failure']),('layout-before',['--hud-before'])]:
    target=OUTPUT/(name+'-execution.json')
    assert not target.exists(),target
    argv=base+(['--']+extra if extra else [])
    p=subprocess.run(argv,capture_output=True,timeout=60)
    (OUTPUT/(name+'-stdout.bin')).write_bytes(p.stdout)
    (OUTPUT/(name+'-stderr.bin')).write_bytes(p.stderr)
    # Godot Windows pipe writes Korean with the active ANSI code page (CP949).
    # Preserve byte streams before decoding; never replace invalid bytes silently.
    stdout=p.stdout.decode('cp949')
    stderr=p.stderr.decode('cp949')
    target.write_text(json.dumps({'argv':argv,'actual_exit':p.returncode,'stdout':stdout,'stderr':stderr,'raw_encoding':'cp949','raw_stdout':name+'-stdout.bin','raw_stderr':name+'-stderr.bin'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(name,p.returncode,'stderr_bytes',len(p.stderr))
