from pathlib import Path
import json,shutil,subprocess,hashlib
B=Path('C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01');S=B/'actor28/motion02/shots';O=B/'actor28/motion02/film01';assert not O.exists();O.mkdir()
for revision in ['25b','28']:
 lines=[]
 for direction in ['north','east','south','west']:
  for repeat in range(2):
   for age in [0,2,4,6,8,10,12,18]:
    path=S/f'{revision}-{direction}-{age:02}.png';assert path.exists();lines.extend([f"file '{path.as_posix()}'",'duration 0.12'])
 lines.append(f"file '{path.as_posix()}'");(O/f'{revision}.concat.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
exe=shutil.which('ffmpeg');assert exe;video=O/'sampled-hit-before-after.mp4'
cmd=[exe,'-v','warning','-n','-f','concat','-safe','0','-i',str(O/'25b.concat.txt'),'-f','concat','-safe','0','-i',str(O/'28.concat.txt'),'-filter_complex','[0:v]scale=960:540[a];[1:v]scale=960:540[b];[a][b]hstack=inputs=2[v]','-map','[v]','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-r','30','-an','-movflags','+faststart',str(video)]
with (O/'stdout.txt').open('xb') as out,(O/'stderr.txt').open('xb') as err:result=subprocess.run(cmd,stdout=out,stderr=err,timeout=90)
assert result.returncode==0
(O/'RESULT.json').write_text(json.dumps(dict(exit=result.returncode,command=cmd,sha256=hashlib.sha256(video.read_bytes()).hexdigest(),scope='Left source25b/right source28 refined fixture02. Four copied roles; north/east/south/west, two repeats each. Eight nonuniform simulation-age samples per reaction, each held0.12s. Deliberate slowed sampled-pose comparison, NOT real-time or continuous captured gameplay. No audio.'),indent=2),encoding='utf-8');print(video,flush=True)
