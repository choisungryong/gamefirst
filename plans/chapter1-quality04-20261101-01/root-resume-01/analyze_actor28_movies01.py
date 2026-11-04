from pathlib import Path
import json,shutil,subprocess,hashlib
B=Path('C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01');O=B/'actor28/normal-film01';D=O/'analysis01';assert not D.exists();D.mkdir()
ffmpeg=Path(shutil.which('ffmpeg'));probe=ffmpeg.with_name('ffprobe.exe');assert probe.exists();rows=[]
for variant in ['control','after']:
 video=O/variant/'normal-speed.mp4';raw=O/variant/'normal-speed.avi'
 cmd=[str(probe),'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)];p=subprocess.run(cmd,capture_output=True,text=True,timeout=60);assert p.returncode==0;metadata=json.loads(p.stdout);(D/f'{variant}-ffprobe.json').write_text(p.stdout,encoding='utf-8')
 result=json.loads((O/variant/'RESULT.json').read_text());visual=next(s for s in metadata['streams'] if s['codec_type']=='video')
 rows.append(dict(variant=variant,tick=result['tick'],core_equal=result['same_complete_core'],hit_blends=result['hit28_blends'],fps=visual['avg_frame_rate'],frames=int(visual['nb_read_frames']),width=visual['width'],height=visual['height'],duration=metadata['format']['duration'],raw_bytes=raw.stat().st_size,video_sha256=hashlib.sha256(video.read_bytes()).hexdigest()))
 for second in [1,2,3]:
  target=D/f'{variant}-{second}s.png';cmd=[str(ffmpeg),'-v','error','-n','-ss',str(second),'-i',str(video),'-frames:v','1',str(target)];p=subprocess.run(cmd,capture_output=True,text=True,timeout=30);assert p.returncode==0,p.stderr
assert rows[0]['tick']==rows[1]['tick'] and rows[0]['frames']==rows[1]['frames']
(D/'RESULT.json').write_text(json.dumps(dict(runs=rows,scope='Continuous60fps offline MovieMaker capture, normal playback speed4simsec per arm. Compare actual final tick/frame counts, not inherited raw RESULT scope text saying10simsec. Raw scope text was inherited from older10sec observer and is not the movie duration. Not real-time performance or manual.',keyframes='1s/2s/3s extracted per arm; direct review recorded separately.'),indent=2),encoding='utf-8');print(json.dumps(rows),flush=True)
