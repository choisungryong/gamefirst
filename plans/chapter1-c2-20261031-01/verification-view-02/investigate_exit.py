from pathlib import Path
import json
import subprocess

root=Path('C:/Project/d2r-combat-baseline')
here=Path(__file__).resolve().parent
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
out=here/'verbose-original-execution.json'
log=here/'verbose-original-godot.log'
assert not out.exists() and not log.exists()
cmd=[engine,'--headless','--verbose','--path',str(root),'--log-file',str(log),'--script','res://plans/chapter1-c2-20261031-01/verification-view-02/independent_view.gd']
r=subprocess.run(cmd,cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=60)
out.write_text(json.dumps({'command':cmd,'actual_exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(r.returncode,r.stdout[-3500:],r.stderr[-3500:])
