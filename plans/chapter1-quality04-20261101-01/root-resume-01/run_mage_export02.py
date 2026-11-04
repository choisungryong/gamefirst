from pathlib import Path
import subprocess,json
HERE=Path(__file__).resolve().parent
source=HERE/'mage_export_research.py';target=HERE/'mage_export_research02.py'
assert not target.exists()
s=source.read_text(encoding='utf-8').replace("/gltf-preview-01')","/gltf-preview-02')")
s=s.replace("for obj in [root,mesh,deform]:obj.select_set(True)","for collection in bpy.data.collections:collection.hide_viewport=False\nfor obj in [root,mesh,deform]:\n    obj.hide_viewport=False;obj.hide_set(False);obj.select_set(True)")
target.write_text(s,encoding='utf-8')
command=['C:/Project/rea-tools/blender-4.5.15-windows-x64/blender.exe','--background','--disable-autoexec',
 'C:/Project/game-research/art-sources/oga-mage-20261101-01/motion-preview-01/mage_motion_research.blend','--python-exit-code','1','--python',str(target)]
r=subprocess.run(command,capture_output=True,timeout=180)
data={'command':command,'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace'),
 'prior_attempt':'gltf-preview-01 preserved, actual1: hidden deform armature prevented exporter mode_set; baking matrix checks passed before export failure'}
with (HERE/'mage-export02-execution.json').open('x',encoding='utf-8') as f:json.dump(data,f,indent=2)
print(json.dumps(data))
