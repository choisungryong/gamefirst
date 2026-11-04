from pathlib import Path
import json,hashlib,shutil,subprocess,re
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';HERE=Path(__file__).parent;OUT=BASE/'elements15/replay02';assert not OUT.exists();OUT.mkdir()
ENGINE='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):assert not p.exists();p.write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
def run(label,cmd,timeout=180,encoder=False):
 with(OUT/(label+'.stdout.txt')).open('xb')as stdout,(OUT/(label+'.stderr.txt')).open('xb')as stderr:
  p=subprocess.Popen(cmd,stdout=stdout,stderr=stderr);write(OUT/(label+'-launch.json'),{'pid':p.pid,'command':cmd});print(json.dumps({'label':label,'pid':p.pid}),flush=True);code=p.wait(timeout=timeout)
 r={'actual_exit':code,'stderr_bytes':(OUT/(label+'.stderr.txt')).stat().st_size};write(OUT/(label+'-execution.json'),r);assert code==0 and not r['stderr_bytes'],(label,r);return r
results={}
pins=json.loads((BASE/'full14/build/staging-manifest.json').read_text(encoding='utf-8'));old=Path('C:/Project/game-research/build-staging/chapter1-full-candidate-20261101-14')
for variant in ['before14','after15']:
 stage=Path('C:/Project/game-research/build-staging/cold-replay-20261101-02-'+variant);assert not stage.exists();stage.mkdir()
 for n,h in pins.items():
  assert sha(old/n)==h
  p=stage/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
 if variant=='after15':
  shutil.copy2(ROOT/'chapter1/view/chapter_elements_quality15.gd',stage/'chapter1/view/chapter_elements_quality15.gd')
  p=stage/'chapter1/chapter_one_view.gd';p.write_text(p.read_text(encoding='utf-8').replace('chapter_elements_quality14.gd','chapter_elements_quality15.gd'),encoding='utf-8')
 p=stage/'project.godot';s=p.read_text(encoding='utf-8').replace('Quality14','ColdReplay02'+variant)
 for key,value in [('viewport_width',1280),('viewport_height',720),('window_width_override',1280),('window_height_override',720)]:s=re.sub(key+r'=\d+',key+'='+str(value),s)
 p.write_text(s,encoding='utf-8');shutil.copy2(HERE/'cold_replay15.gd',stage/'cold_replay.gd')
 (stage/'ColdReplay.tscn').write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://cold_replay.gd" id="1"]\n[node name="ColdReplay" type="Node3D"]\nscript=ExtResource("1")\n',encoding='utf-8')
 frozen={str(p.relative_to(stage)).replace('\\','/'):sha(p)for p in stage.rglob('*')if p.is_file()};write(OUT/(variant+'-source.json'),{'stage':str(stage),'pins':frozen,'scope':'Same normal policy core resimulated120s, defaultHP/earnedrank; clear cosmetic boundary then18s offline30FPS. Discard first1s.'})
 run(variant+'-import',[ENGINE,'--headless','--path',str(stage),'--editor','--import'])
 run(variant+'-check',[ENGINE,'--headless','--path',str(stage),'--check-only','--script','res://cold_replay.gd'])
 movie=OUT/(variant+'.avi')
 run(variant+'-movie',[ENGINE,'--path',str(stage),'res://ColdReplay.tscn','--write-movie',str(movie),'--fixed-fps','30','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--chapter1-qa-ignore-focus','--chapter1-quit-after=18','--replay-variant='+variant],240)
 start=json.loads((stage/'replay-start.json').read_text(encoding='utf-8'));result=json.loads((stage/'replay-result.json').read_text(encoding='utf-8'))
 write(OUT/(variant+'-start.json'),start);write(OUT/(variant+'-result.json'),result)
 shutil.copytree(stage/'replay-captures',OUT/(variant+'-captures'))
 assert all(sha(stage/n)==h for n,h in frozen.items());results[variant]={'movie':str(movie),'sha256':sha(movie),'start':start,'result':result}
assert results['before14']['start']==results['after15']['start']
assert results['before14']['result']['core']==results['after15']['result']['core']
assert results['after15']['result']['cosmetic_death_accents']>0
ffmpeg=shutil.which('ffmpeg');ffprobe=shutil.which('ffprobe');assert ffmpeg and ffprobe
movie=OUT/'normal-cold-before14-after15-16s.mp4'
filters="[0:v]trim=start=1:duration=16,setpts=PTS-STARTPTS,scale=640:360,pad=640:428:0:36:color=0x11191f[l];[1:v]trim=start=1:duration=16,setpts=PTS-STARTPTS,scale=640:360,pad=640:428:0:36:color=0x11191f[r];[l][r]hstack,drawtext=text='BEFORE 14':x=18:y=6:fontsize=22:fontcolor=white,drawtext=text='AFTER 15':x=658:y=6:fontsize=22:fontcolor=white,drawtext=text='Normal-policy replay from120s / defaultHP + earnedbuild / OFFLINE30FPS / right audio only':x=18:y=401:fontsize=16:fontcolor=0xc5d2d8[out]"
run('compose',[ffmpeg,'-hide_banner','-loglevel','error','-nostdin','-i',results['before14']['movie'],'-i',results['after15']['movie'],'-filter_complex',filters,'-map','[out]','-map','1:a:0?','-af','atrim=start=1:duration=16,asetpts=PTS-STARTPTS','-t','16','-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(movie)])
p=subprocess.run([ffprobe,'-v','error','-show_streams','-show_format','-of','json',str(movie)],capture_output=True,text=True,encoding='utf-8');assert p.returncode==0 and not p.stderr;write(OUT/'ffprobe.json',json.loads(p.stdout))
write(OUT/'COMPARISON.json',{'same_full_core_start_and_end':True,'results':results,'comparison_mp4':str(movie),'sha256':sha(movie),'scope':'Normal defaultHP/earned build, ordinary policy core resimulated120s then18s offline30FPS replay; cosmetic boundary starts clear and first1s discarded. Event-synchronous captures. Not realtime/fullchapter/manual/audio/performance/art approval.'});print(json.dumps({'movie':str(movie),'core_same':True,'after_accents':results['after15']['result']['cosmetic_death_accents']}),flush=True)
