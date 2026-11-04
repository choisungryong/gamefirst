from pathlib import Path
import json,shutil,subprocess,hashlib,time,re
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';HERE=Path(__file__).parent;OUT=BASE/'elements14/movie05';assert not OUT.exists();OUT.mkdir()
ENGINE='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 assert not p.exists();p.write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
def run(label,cmd,timeout=180):
 with(OUT/(label+'.stdout.txt')).open('xb')as stdout,(OUT/(label+'.stderr.txt')).open('xb')as stderr:
  p=subprocess.Popen(cmd,stdout=stdout,stderr=stderr);write(OUT/(label+'-launch.json'),{'pid':p.pid,'command':cmd});print(json.dumps({'label':label,'pid':p.pid}),flush=True);code=p.wait(timeout=timeout)
 r={'actual_exit':code,'stderr_bytes':(OUT/(label+'.stderr.txt')).stat().st_size};write(OUT/(label+'-execution.json'),r)
 assert code==0 and not r['stderr_bytes'],(label,r)
 return r
results={}
for variant,n in [('before13',13),('after14',14)]:
 stage=Path('C:/Project/game-research/build-staging/elements-movie-20261101-05-'+variant);assert not stage.exists();stage.mkdir()
 closure=json.loads((BASE/f'full{n}/FINAL-SOURCE-FREEZE.json').read_text(encoding='utf-8'))
 for name,h in closure.items():
  if name in ['project.godot','export_presets.cfg']:continue
  source=ROOT/name if n==14 else Path('C:/Project/game-research/build-staging/chapter1-full-candidate-20261101-13')/name
  assert sha(source)==h,(variant,name)
  dest=stage/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
 project=Path('C:/Project/game-research/build-staging/chapter1-full-candidate-20261101-13/project.godot').read_text(encoding='utf-8').replace('Quality13','ElementsMovie05'+variant)
 for key,value in [('viewport_width',1280),('viewport_height',720),('window_width_override',1280),('window_height_override',720)]:project=re.sub(key+r'=\d+',key+'='+str(value),project)
 (stage/'project.godot').write_text(project,encoding='utf-8')
 shutil.copy2(HERE/'elements_fixture14.gd',stage/'elements_fixture14.gd')
 (stage/'ElementsFixture.tscn').write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://elements_fixture14.gd" id="1"]\n[node name="ElementsFixture" type="Node3D"]\nscript=ExtResource("1")\n',encoding='utf-8')
 pins={str(p.relative_to(stage)).replace('\\','/'):sha(p)for p in stage.rglob('*')if p.is_file()};write(OUT/(variant+'-source.json'),{'stage':str(stage),'pins':pins,'scope':'Configured80enemy arena, supplied evolved frost and arc. Same core and fixed input, GPU offline30FPS, not normal whole chapter or performance.'})
 run(variant+'-import',[ENGINE,'--headless','--path',str(stage),'--editor','--import'])
 movie=OUT/(variant+'.avi')
 run(variant+'-movie',[ENGINE,'--path',str(stage),'res://ElementsFixture.tscn','--write-movie',str(movie),'--fixed-fps','30','--','--chapter1-profile-off','--chapter1-start','--chapter1-qa-ignore-focus','--chapter1-quit-after=14','--elements-variant='+variant])
 result=json.loads((stage/'elements-result.json').read_text(encoding='utf-8'));write(OUT/(variant+'-result.json'),result)
 assert all(sha(stage/n)==h for n,h in pins.items())
 results[variant]={'movie':str(movie),'sha256':sha(movie),'bytes':movie.stat().st_size,'result':result}
same={k:results['before13']['result'][k]==results['after14']['result'][k]for k in ['tick','kills','counts','max_frozen','metrics','hero','growth']};assert all(same.values()),same
ffmpeg=shutil.which('ffmpeg');ffprobe=shutil.which('ffprobe');assert ffmpeg and ffprobe
target=OUT/'elements-before13-after14-13s.mp4';assert not target.exists()
filters="[0:v]trim=duration=13,setpts=PTS-STARTPTS,scale=640:360,pad=640:428:0:36:color=0x11191f[l];[1:v]trim=duration=13,setpts=PTS-STARTPTS,scale=640:360,pad=640:428:0:36:color=0x11191f[r];[l][r]hstack,drawtext=text='BEFORE 13':x=18:y=6:fontsize=22:fontcolor=white,drawtext=text='AFTER 14':x=658:y=6:fontsize=22:fontcolor=white,drawtext=text='Configured arena / supplied build / same inputs / OFFLINE 30 FPS / right audio only':x=18:y=401:fontsize=18:fontcolor=0xc5d2d8[out]"
cmd=[ffmpeg,'-hide_banner','-nostdin','-i',results['before13']['movie'],'-i',results['after14']['movie'],'-filter_complex',filters,'-map','[out]','-map','1:a:0?','-t','13','-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(target)]
run('compose',cmd)
probe=subprocess.run([ffprobe,'-v','error','-show_streams','-show_format','-of','json',str(target)],capture_output=True,text=True,encoding='utf-8');assert probe.returncode==0;write(OUT/'ffprobe.json',json.loads(probe.stdout))
write(OUT/'COMPARISON.json',{'same_core_arena':same,'results':results,'comparison_mp4':str(target),'sha256':sha(target),'scope':'Own-game configured arena before13 vs14, offline30FPS and right audio only, no heard-audio/manual/full-chapter/performance or final art approval.'});print(json.dumps({'movie':str(target),'same':same,'sha256':sha(target)}),flush=True)
