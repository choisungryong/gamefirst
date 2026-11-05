from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent;O=B/'full35/runtime/default-profile-earn01';assert not O.exists();O.mkdir()
profile=Path('C:/Users/twins/AppData/Roaming/AshenCloisterChapterOneQuality35/chapter-one-profile-v1.json');assert not profile.exists(),'Preserve existing default profile; review before running'
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();build=read(B/'full35/build/build.json');exe=Path(build['exe']);assert sha(exe)==build['sha256'];script=H/'default_profile35_earn.gd';shutil.copy2(script,O/script.name);runtime=exe.parent/'qa-probe/default-profile-earn01';assert not runtime.exists()
for label,args in [('check',['--headless','--check-only','--script',str(script)]),('earned',['--headless','--fixed-fps','60','--script',str(script),'--','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--profile35-dir='+str(runtime)])]:
 with (O/(label+'.stdout.txt')).open('xb') as stdout,(O/(label+'.stderr.txt')).open('xb') as stderr:
  cmd=[str(exe)]+args;p=subprocess.Popen(cmd,stdout=stdout,stderr=stderr);(O/(label+'-launch.json')).write_text(json.dumps(dict(pid=p.pid,command=cmd,exe_sha256=sha(exe)),indent=2));print(label,p.pid,flush=True);code=p.wait(timeout=270)
 result=dict(exit=code,stderr_bytes=(O/(label+'.stderr.txt')).stat().st_size);(O/(label+'-execution.json')).write_text(json.dumps(result));assert result==dict(exit=0,stderr_bytes=0),result
shutil.copytree(runtime,O/'proof');result=read(O/'proof/RESULT.json');assert result['saved'] and result['same_profile_after_reload'] and result['same_complete_core'] and Path(result['absolute_profile_path'])==profile
saved=O/'default-profile-preserved';saved.mkdir();pins={}
for p in profile.parent.glob('chapter-one-profile-v1*.json'):shutil.copy2(p,saved/p.name);pins[p.name]=sha(p)
(O/'PROFILE-PINS.json').write_text(json.dumps(dict(path=str(profile.parent),pins=pins,initial_profile_absent=True,scope='Newly earned actual default35 profile and journals preserved. Never delete or reset as a disposable fixture.'),indent=2));assert sha(exe)==build['sha256'];print('ACTUAL35 DEFAULT EARN/SAVE/RELOAD PASS; USER PROFILE PRESERVED',flush=True)
