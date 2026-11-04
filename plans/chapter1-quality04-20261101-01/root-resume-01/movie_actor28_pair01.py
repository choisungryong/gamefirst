from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'actor28/normal-film01';assert not O.exists();O.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=read(B/'actor28/replay01/source.json');old=Path(source['stage']);assert all(sha(old/n)==h for n,h in source['pins'].items())
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe';ffmpeg=shutil.which('ffmpeg');assert ffmpeg
for variant in ['control','after']:
 out=O/variant;out.mkdir();stage=Path(f'C:/Project/game-research/build-staging/chapter1-actor28-normal-film-{variant}01');assert not stage.exists();stage.mkdir()
 for n,h in source['pins'].items():
  p=stage/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
 script=stage/'compare.gd';s=script.read_text(encoding='utf-8').replace('actors.hit28_blends','actors.get("hit28_blends")')
 if variant=='control':s=s.replace('chapter_actors_quality28.gd','chapter_actors_quality25b.gd')
 script.write_text(s,encoding='utf-8');pins={n:sha(stage/n) for n in source['pins']};(out/'source.json').write_text(json.dumps(dict(stage=str(stage),pins=pins),indent=2))
 raw=out/'normal-speed.avi'
 phases=[('import',['--headless','--editor','--import']),('gpu',['res://Compare.tscn','--resolution','1280x720','--write-movie',str(raw),'--fixed-fps','60','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.ember','--chapter1-seed=90131','--chapter1-quit-after=4'])]
 for label,args in phases:
  with (out/(label+'.stdout.txt')).open('xb') as stdout,(out/(label+'.stderr.txt')).open('xb') as stderr:
   cmd=[engine,'--path',str(stage)]+args;p=subprocess.Popen(cmd,stdout=stdout,stderr=stderr);(out/(label+'-launch.json')).write_text(json.dumps(dict(pid=p.pid,command=cmd),indent=2));print(variant,label,p.pid,flush=True);code=p.wait(timeout=180)
  result=dict(exit=code,stderr_bytes=(out/(label+'.stderr.txt')).stat().st_size);(out/(label+'-execution.json')).write_text(json.dumps(result));assert result==dict(exit=0,stderr_bytes=0),result
 shutil.copy2(stage/'actor28-result.json',out/'RESULT.json');assert read(out/'RESULT.json')['same_complete_core'];assert all(sha(stage/n)==h for n,h in pins.items())
 mp4=out/'normal-speed.mp4';cmd=[ffmpeg,'-v','warning','-n','-i',str(raw),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart',str(mp4)]
 with (out/'encode.stdout.txt').open('xb') as stdout,(out/'encode.stderr.txt').open('xb') as stderr:code=subprocess.run(cmd,stdout=stdout,stderr=stderr,timeout=90).returncode
 assert code==0;print(variant,'MOVIE PASS',mp4.stat().st_size,flush=True)
assert all(sha(R/n)==h for n,h in read(B/'full27/FINAL-SOURCE-FREEZE.json').items())
(O/'SCOPE.json').write_text(json.dumps(dict(scope='Source27 normal earned ember16000tick policy, continuous MovieMaker60fps recordings4simsec each. Control Actor25b/after Actor28. Normal playback speed, offline fixed-step render NOT real-time performance/manual. Original game audio captured but not hearing-approved.',official_reference='https://docs.godotengine.org/en/4.5/tutorials/animation/creating_movies.html'),indent=2));print('PAIRED NORMAL SPEED MOVIES COMPLETE',flush=True)
