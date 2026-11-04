from pathlib import Path
import json,hashlib,subprocess,shutil
ROOT=Path('C:/Project/d2r-combat-baseline');OUT=ROOT/'plans/chapter1-quality04-20261101-01/elements14/movie05'
def write(p,v):assert not p.exists();p.write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
same={};results={}
for variant in ['before13','after14']:
 r=json.loads((OUT/(variant+'-movie-execution.json')).read_text(encoding='utf-8'));assert r['actual_exit']==0 and not r['stderr_bytes']
 state=json.loads((OUT/(variant+'-result.json')).read_text(encoding='utf-8'));movie=OUT/(variant+'.avi')
 results[variant]={'movie':str(movie),'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'bytes':movie.stat().st_size,'result':state}
same={k:results['before13']['result'][k]==results['after14']['result'][k]for k in ['tick','kills','counts','max_frozen','metrics','hero','growth']};assert all(same.values())
execution=json.loads((OUT/'compose-execution.json').read_text(encoding='utf-8'));assert execution['actual_exit']==0
mp4=OUT/'elements-before13-after14-13s.mp4';ffprobe=shutil.which('ffprobe');assert ffprobe
p=subprocess.run([ffprobe,'-v','error','-show_streams','-show_format','-of','json',str(mp4)],capture_output=True,text=True,encoding='utf-8');assert p.returncode==0 and not p.stderr
probe=json.loads(p.stdout);video=next(s for s in probe['streams']if s['codec_type']=='video');assert video['codec_name']=='h264'and video['width']==1280 and video['height']==428 and abs(float(probe['format']['duration'])-13)<.1 and int(video['nb_frames'])==390
write(OUT/'ffprobe.json',probe)
write(OUT/'COMPARISON.json',{'same_core_arena':same,'results':results,'comparison_mp4':str(mp4),'sha256':hashlib.sha256(mp4.read_bytes()).hexdigest(),'encoder_review':'compose exited0 and emitted normal ffmpeg/libx264 progress to stderr; original helper incorrectly required empty stderr. No re-encode or overwritten evidence. ffprobe confirms H2641280x428/390frames/13s.','scope':'Configured arena, supplied evolved loadout, offline30FPS, right audio only; no normal whole chapter/manual/heard-audio/performance or final art approval.'})
print(json.dumps({'movie':str(mp4),'same':same,'duration':probe['format']['duration']}),flush=True)
