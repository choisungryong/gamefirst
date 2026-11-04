from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'motion32/mapped02';S=Path('C:/Project/game-research/build-staging/chapter1-motion32-mapped02');assert not O.exists() and not S.exists();O.mkdir(parents=True);S.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=Path(read(B/'full31/build/closure.json')['stage'])
for n,h in read(B/'full31/build/staging-manifest.json').items():
 assert sha(old/n)==h
 p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
shutil.copy2(R/'chapter1/view/chapter_actors_quality32b.gd',S/'chapter1/view/chapter_actors_quality32b.gd');shutil.copy2(H/'motion32_mapped.gd',S/'mapped.gd')
pins={str(p.relative_to(S)).replace('\\','/'):sha(p) for p in S.rglob('*') if p.is_file()};(O/'source.json').write_text(json.dumps(dict(stage=str(S),pins=pins),indent=2))
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe';ffmpeg=shutil.which('ffmpeg');assert ffmpeg
phases=[('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://mapped.gd'])]
for variant in ['32b']:phases.append((variant,['--script','res://mapped.gd','--resolution','960x540','--fixed-fps','60','--','--chapter1-profile-off','--chapter1-start','--chapter1-primary=chapter1.skill.ember','--chapter1-seed=90131','--mapped-dir='+str(O/variant),'--mapped-actor='+variant]))
for label,args in phases:
 with (O/(label+'.stdout.txt')).open('xb') as stdout,(O/(label+'.stderr.txt')).open('xb') as stderr:
  cmd=[engine,'--path',str(S)]+args;p=subprocess.Popen(cmd,stdout=stdout,stderr=stderr);(O/(label+'-launch.json')).write_text(json.dumps(dict(pid=p.pid,command=cmd),indent=2));print(label,p.pid,flush=True);code=p.wait(timeout=240)
 d=dict(exit=code,stderr_bytes=(O/(label+'.stderr.txt')).stat().st_size);(O/(label+'-execution.json')).write_text(json.dumps(d));assert d==dict(exit=0,stderr_bytes=0),d
 if label in ['32b']:
  for phase,count in [('normal',120),('attack',180)]:
   cmd=[ffmpeg,'-v','warning','-n','-framerate','60','-i',str(O/label/(phase+'-%03d.png')),'-frames:v',str(count),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(O/label/(phase+'.mp4'))]
   with (O/f'{label}-{phase}-encode.stdout.txt').open('xb') as stdout,(O/f'{label}-{phase}-encode.stderr.txt').open('xb') as stderr:result=subprocess.run(cmd,stdout=stdout,stderr=stderr,timeout=90)
   assert result.returncode==0
before=read(B/'motion32/mapped01/30c/RESULT.json');after=read(O/'32b/RESULT.json');checks={}
checks['normal_end_core_equal']=before['normal_core']==after['normal_core'];checks['original_core_restored']=before['complete_normal_core_restored'] and after['complete_normal_core_restored'];checks['rows300_each']=len(before['rows'])==300 and len(after['rows'])==300
checks['every_frame_same_core']=all((a['phase'],a['frame'],a['tick'],a['core_sha256'])==(d['phase'],d['frame'],d['tick'],d['core_sha256']) for a,d in zip(before['rows'],after['rows']))
checks['normal_exact_ticks']=all(r['tick']==16001+r['frame'] for r in after['rows'] if r['phase']=='normal');checks['hit_blends']=after['hit_blends']>0;checks['source_immutable']=all(sha(S/n)==h for n,h in pins.items());checks['root31_frozen']=all(sha(R/n)==h for n,h in read(B/'full31/FINAL-SOURCE-FREEZE.json').items())
(O/'COMPARISON.json').write_text(json.dumps(dict(checks=checks,passed=all(checks.values()),scope='Own per-frame PNGs encoded60fps, map300 rows per arm;120 normal core steps+180 copied role attack frames. No startup/cleanup frames encoded; source QA not package/manual/performance.'),indent=2));print(checks,flush=True);assert all(checks.values())
