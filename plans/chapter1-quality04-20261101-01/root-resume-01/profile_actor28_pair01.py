from pathlib import Path
import json,hashlib,shutil,subprocess,statistics
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';H=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
for variant in ['control','after']:
 s=(H/'hit26_profile_control01.gd').read_text(encoding='utf-8').replace('hit26_blends','hit28_blends')
 if variant=='after':s=s.replace('extends "res://chapter1/view/chapter_actors_quality25b.gd"','extends "res://chapter1/view/chapter_actors_quality28.gd"')
 script=H/f'actor28_profile_{variant}01.gd';assert not script.exists();script.write_text(s,encoding='utf-8')
 wrapper=(H/'run_hit26_profile_control01.py').read_text(encoding='utf-8').replace('hit26/profile-control01',f'actor28/profile-{variant}01').replace('chapter1-hit26-profile-control01',f'chapter1-actor28-profile-{variant}01').replace('full25b','full27').replace('chapter_actors_quality26.gd','chapter_actors_quality28.gd').replace('hit26_profile_control01.gd',script.name)
 path=H/f'run_actor28_profile_{variant}01.py';assert not path.exists();path.write_text(wrapper,encoding='utf-8')
 exec(compile(wrapper,str(path),'exec'))
 d=read(B/f'actor28/profile-{variant}01/RESULT.json');samples=d['rows'];rows.append(dict(variant=variant,tick=d['tick'],samples=len(samples),actors_mean_ms=statistics.mean(x['actors_us'] for x in samples)/1000,actors_max_ms=max(x['actors_us'] for x in samples)/1000,process_max_ms=max(x['process_us'] for x in samples)/1000,physics_max_ms=max(x['physics_us'] for x in samples)/1000,hit_blends=d['hit_blends'],core_equal=d['same_complete_core'],pool_created=d['pool_created'],pool_hits=d['pool_hits']))
out=B/'actor28/CPU-COMPARISON01.json';assert not out.exists();out.write_text(json.dumps(dict(runs=rows,scope='Matched source27 components, normal ember2800->3400tick, fixed60 GPU each once. Actor25b vs28 CPU callback attribution; NOT real-time frame pacing/final performance approval.'),indent=2));print(json.dumps(rows),flush=True)
