from pathlib import Path
import subprocess,shutil,json,hashlib
HERE=Path(__file__).parent
ffmpeg=shutil.which('ffmpeg');ffprobe=shutil.which('ffprobe');assert ffmpeg and ffprobe
def run(label,cmd):
 r=subprocess.run(cmd,capture_output=True,timeout=180)
 with(HERE/(label+'.json')).open('x',encoding='utf-8')as f:json.dump({'command':cmd,'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace')},f,indent=2)
 assert r.returncode==0
 return r
for name in ['sprite09','rigged05']:
 run(name+'-encode',[ffmpeg,'-n','-i',str(HERE/(name+'.avi')),'-t','24','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(HERE/(name+'.mp4'))])
 for second in [5,10,20]:run(name+'-frame-'+str(second),[ffmpeg,'-n','-ss',str(second),'-i',str(HERE/(name+'.mp4')),'-frames:v','1',str(HERE/(name+'-%02d.png'%second))])
font="fontfile='C\\:/Windows/Fonts/arial.ttf'"
left='[0:v]scale=960:540,pad=960:588:0:48:black,drawtext='+font+":text='SPRITE 09 - OFFLINE 30 FPS':x=16:y=14:fontsize=19:fontcolor=white[l]"
right='[1:v]scale=960:540,pad=960:588:0:48:black,drawtext='+font+":text='RIGGED 05 - OFFLINE 30 FPS - AUDIO 05':x=16:y=14:fontsize=19:fontcolor=white[r]"
out=HERE/'hero-comparison-24s.mp4'
run('side-by-side',[ffmpeg,'-n','-i',str(HERE/'sprite09.mp4'),'-i',str(HERE/'rigged05.mp4'),'-filter_complex',left+';'+right+';[l][r]hstack=inputs=2[v]','-map','[v]','-map','1:a:0','-t','24','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(out)])
metadata=json.loads(run('comparison-probe',[ffprobe,'-v','error','-show_format','-show_streams','-of','json',str(out)]).stdout)
assert abs(float(metadata['format']['duration'])-24)<.1
with(HERE/'MOVIES.json').open('x',encoding='utf-8')as f:json.dump({'scope':'Own-game GPU offline fixed30FPS. No real-time/manual/audio approval. Gameplay states identical. Compared exact first24s; shutdown held frames trimmed.','metadata':metadata,'artifacts':{p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}for p in HERE.glob('*.mp4')}},f,indent=2)
print(json.dumps({'comparison':str(out),'duration':metadata['format']['duration']}))
