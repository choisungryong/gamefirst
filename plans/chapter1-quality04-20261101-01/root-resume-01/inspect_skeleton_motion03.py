from pathlib import Path
import subprocess,shutil,json
STAGE=Path('C:/Project/game-research/build-staging/skeleton-outlaw-import-20261101-02')
OUT=Path('C:/Project/game-research/art-sources/oga-skeleton-outlaw-20261101-01/godot-convert02')
target=STAGE/'motion.gd';assert not target.exists();shutil.copy2(Path(__file__).with_name('skeleton_motion_inventory03.gd'),target)
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('derived-import',['--editor','--import']),('motion-inventory',['--script','res://motion.gd'])]:
 command=[engine,'--headless','--path',str(STAGE)]+args;r=subprocess.run(command,capture_output=True,timeout=120)
 with(OUT/(label+'-execution.json')).open('x',encoding='utf-8')as f:json.dump({'command':command,'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace')},f,indent=2)
 print(json.dumps({'label':label,'actual_exit':r.returncode,'stderr':r.stderr.decode('utf-8','replace')[:1200]}),flush=True)
 assert r.returncode==0 and not r.stderr
shutil.copy2(STAGE/'motion-inventory03.json',OUT/'motion-inventory03.json')
print((OUT/'motion-inventory03.json').read_text(encoding='utf-8'))
