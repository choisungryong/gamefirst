from pathlib import Path
import json,hashlib,shutil,subprocess,re
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'cold16/actors-movie02'
assert not OUT.exists();OUT.mkdir()
ENGINE='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
    assert not p.exists();p.write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
def run(label,cmd,timeout=240):
    with (OUT/(label+'.stdout.txt')).open('xb') as o,(OUT/(label+'.stderr.txt')).open('xb') as e:
        p=subprocess.Popen(cmd,stdout=o,stderr=e);write(OUT/(label+'-launch.json'),{'pid':p.pid,'command':cmd});print(label,p.pid,flush=True);code=p.wait(timeout=timeout)
    result={'exit':code,'stderr_bytes':(OUT/(label+'.stderr.txt')).stat().st_size};write(OUT/(label+'-execution.json'),result)
    assert code==0 and result['stderr_bytes']==0,(label,result)
results={}
for variant in ['before','after']:
    pins=json.loads((BASE/'cold16/actors01'/(variant+'-source.json')).read_text(encoding='utf-8'))
    old=Path(pins['stage']);stage=Path('C:/Project/game-research/build-staging/chapter1-cold16-actors-movie02-'+variant)
    assert not stage.exists();stage.mkdir()
    for n,h in pins['pins'].items():
        assert sha(old/n)==h
        p=stage/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
    p=stage/'project.godot';s=p.read_text(encoding='utf-8')
    for key,value in [('viewport_width',1280),('viewport_height',720),('window_width_override',1280),('window_height_override',720)]:s=re.sub(key+r'=\d+',key+'='+str(value),s)
    p.write_text(s,encoding='utf-8')
    frozen={str(p.relative_to(stage)).replace('\\','/'):sha(p) for p in stage.rglob('*') if p.is_file()};write(OUT/(variant+'-source.json'),{'stage':str(stage),'pins':frozen})
    run(variant+'-import',[ENGINE,'--headless','--path',str(stage),'--editor','--import'])
    movie=OUT/(variant+'.avi')
    run(variant+'-movie',[ENGINE,'--path',str(stage),'res://ActorReplay.tscn','--write-movie',str(movie),'--fixed-fps','30','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--chapter1-qa-ignore-focus','--chapter1-quit-after=8'])
    results[variant]={}
    for name in ['start','end','checks']:
        v=json.loads((stage/(name+'.json')).read_text(encoding='utf-8'));results[variant][name]=v;write(OUT/(variant+'-'+name+'.json'),v)
    shutil.copytree(stage/'shots',OUT/(variant+'-shots'))
    assert all(sha(stage/n)==h for n,h in frozen.items())
assert results['before']['start']==results['after']['start'] and results['before']['end']==results['after']['end']
assert all(results['after']['checks'].values())
ffmpeg=shutil.which('ffmpeg');ffprobe=shutil.which('ffprobe');assert ffmpeg and ffprobe
movie=OUT/'cold16-corpse-before-after-6s.mp4'
filters="[0:v]trim=start=1:duration=6,setpts=PTS-STARTPTS,scale=640:360,pad=640:428:0:36:color=0x11191f[l];[1:v]trim=start=1:duration=6,setpts=PTS-STARTPTS,scale=640:360,pad=640:428:0:36:color=0x11191f[r];[l][r]hstack,drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='COLD16 - OLD CORPSES':x=18:y=6:fontsize=22:fontcolor=white,drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='COLD16 - NEW CORPSES':x=658:y=6:fontsize=22:fontcolor=white,drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='Same rules + seed / normal policy from54s / default HP + earned build / OFFLINE30FPS / right audio':x=18:y=401:fontsize=15:fontcolor=0xc5d2d8[out]"
run('compose',[ffmpeg,'-hide_banner','-loglevel','error','-nostdin','-i',str(OUT/'before.avi'),'-i',str(OUT/'after.avi'),'-filter_complex',filters,'-map','[out]','-map','1:a:0?','-af','atrim=start=1:duration=6,asetpts=PTS-STARTPTS','-t','6','-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(movie)])
p=subprocess.run([ffprobe,'-v','error','-show_streams','-show_format','-of','json',str(movie)],capture_output=True,text=True,encoding='utf-8');assert p.returncode==0 and not p.stderr
write(OUT/'ffprobe.json',json.loads(p.stdout))
write(OUT/'COMPARISON.json',{'same_full_core_start_and_end':True,'movie':str(movie),'sha256':sha(movie),'checks':results['after']['checks'],'scope':'Same cold16 rule before/after corpse presentation. Normal policy seed90131/defaultHP/earned build, resimulated54s then8s offline30FPS. First1s discarded,6s comparison. Not14vs16 gameplay/realtime/manual/fullchapter/heard-audio/performance/art approval.'})
print(str(movie),flush=True)
