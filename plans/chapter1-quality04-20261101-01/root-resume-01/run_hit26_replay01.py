from pathlib import Path
import json,hashlib,subprocess,shutil
r=Path('C:/Project/d2r-combat-baseline');b=r/'plans/chapter1-quality04-20261101-01';o=b/'hit26/replay01';s=Path('C:/Project/game-research/build-staging/chapter1-hit26-replay01');read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (o/'gpu-launch.json').exists();pins=read(o/'source.json')['pins'];assert all(sha(s/n)==v for n,v in pins.items())
cmd=['C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe','--path',str(s),'res://Compare.tscn','--resolution','1920x1080','--fixed-fps','60','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.ember','--chapter1-seed=90131','--chapter1-quit-after=10']
with (o/'gpu.stdout.txt').open('xb') as out,(o/'gpu.stderr.txt').open('xb') as err:
 p=subprocess.Popen(cmd,stdout=out,stderr=err);(o/'gpu-launch.json').write_text(json.dumps({'pid':p.pid,'command':cmd},indent=2));print('gpu',p.pid,flush=True);code=p.wait(timeout=180)
(o/'gpu-execution.json').write_text(json.dumps({'exit':code,'stderr_bytes':(o/'gpu.stderr.txt').stat().st_size}));assert code==0 and (o/'gpu.stderr.txt').stat().st_size==0
shutil.copy2(s/'skin24-result.json',o/'RESULT.json');shutil.copytree(s/'skin24-shots',o/'shots');d=read(o/'RESULT.json');assert d['same_complete_core'] and d['hit26_blends']>0;assert all(sha(s/n)==v for n,v in pins.items());assert all(sha(r/n)==v for n,v in read(b/'full25b/FINAL-SOURCE-FREEZE.json').items());print('PASS HIT26 NORMAL PARTIAL',d['hit26_blends'],flush=True)
