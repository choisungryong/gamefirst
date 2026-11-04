from pathlib import Path
import subprocess,json
HERE=Path(__file__).resolve().parent
source=HERE/'run_mage_godot_preview04.py';target=HERE/'mage_godot_preview05_runner.py';assert not target.exists()
s=source.read_text(encoding='utf-8').replace('mage-gltf-research-20261101-02','mage-gltf-research-20261101-03').replace('gltf-preview-04','gltf-preview-05').replace('mage-godot04-','mage-godot05-')
target.write_text(s,encoding='utf-8')
r=subprocess.run(['C:/Users/twins/AppData/Local/Programs/Python/Python310/python.exe',str(target)],capture_output=True,timeout=150)
with (HERE/'mage-godot05-runner.json').open('x',encoding='utf-8') as f:json.dump({'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace')},f,indent=2)
print(json.dumps({'actual_exit':r.returncode,'stderr':r.stderr.decode('utf-8','replace')}))
