from pathlib import Path
import json,subprocess,shutil,sys
HERE=Path(__file__).parent
STAGE=Path('C:/Project/game-research/build-staging/rigged-hero-20261101-01')
label=sys.argv[1];proof=HERE/label;assert not proof.exists();proof.mkdir()
capture=STAGE/'plans/chapter1-quality04-20261101-01/rigged-hero-01'/label/'captures';assert not capture.exists()
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
command=[engine,'--path',str(STAGE),'--max-fps','120','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-capture-dir='+str(capture),'--chapter1-quit-after=42']
with (proof/'stdout.txt').open('x',encoding='utf-8') as stdout,(proof/'stderr.txt').open('x',encoding='utf-8') as stderr:
 p=subprocess.Popen(command,stdout=stdout,stderr=stderr)
 with (proof/'launch.json').open('x',encoding='utf-8') as f:json.dump({'pid':p.pid,'command':command},f,indent=2)
 print(json.dumps({'pid':p.pid,'proof':str(proof)}),flush=True)
 code=p.wait(timeout=120)
if capture.exists():shutil.copytree(capture,proof/'captures')
with (proof/'execution.json').open('x',encoding='utf-8') as f:json.dump({'actual_exit':code,'stderr_bytes':(proof/'stderr.txt').stat().st_size,'capture_count':len(list(capture.glob('*.png'))) if capture.exists() else 0},f,indent=2)
print(json.dumps({'actual_exit':code,'stderr':(proof/'stderr.txt').read_text(encoding='utf-8',errors='replace')[:2000]}))
