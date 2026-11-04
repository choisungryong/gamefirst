from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=B/'root-resume-01';O=B/'sprite-pipeline01/engine02';S=Path('C:/Project/game-research/build-staging/chapter1-sprite-pipeline02');assert not O.exists() and not S.exists();O.mkdir();S.mkdir();read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=Path(read(B/'full30/build/closure.json')['stage'])
for n,h in read(B/'full30/build/staging-manifest.json').items():
 assert sha(old/n)==h;p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
p=S/'chapter1/presentation/sprite_asset_presenter.gd';shutil.copy2(R/'chapter1/presentation/sprite_asset_presenter.gd',p)
shutil.copytree(B/'sprite-pipeline01/assets',S/'plans/chapter1-quality04-20261101-01/sprite-pipeline01/assets');shutil.copy2(H/'sprite_pipeline_browser_probe.gd',S/'probe.gd');pins={str(p.relative_to(S)).replace('\\','/'):sha(p) for p in S.rglob('*') if p.is_file()};(O/'source.json').write_text(json.dumps(dict(stage=str(S),pins=pins),indent=2));engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://probe.gd']),('headless',['--headless','--script','res://probe.gd']),('gpu',['--script','res://probe.gd','--resolution','1280x720'])]:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  cmd=[engine,'--path',str(S)]+args;p=subprocess.Popen(cmd,stdout=out,stderr=err);(O/(label+'-launch.json')).write_text(json.dumps(dict(pid=p.pid,command=cmd),indent=2));print(label,p.pid,flush=True);code=p.wait(timeout=180)
 result=dict(exit=code,stderr_bytes=(O/(label+'.stderr.txt')).stat().st_size);(O/(label+'-execution.json')).write_text(json.dumps(result));assert result==dict(exit=0,stderr_bytes=0),result
for name in ['sprite-pipeline-headless-result.json','sprite-pipeline-gpu-result.json','sprite-pipeline-preview.png']:shutil.copy2(S/name,O/name)
assert all(sha(S/n)==h for n,h in pins.items());print('SPRITE PIPELINE REAL GODOT PROOF COMPLETE',flush=True)
