from pathlib import Path
import json,hashlib,shutil
r=Path('C:/Project/d2r-combat-baseline');b=r/'plans/chapter1-quality04-20261101-01';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
o=b/'pool25/fixed-fixture01';d=read(o/'RESULT.json');assert len(d['checks'])==50 and all(d['checks'].values());assert read(o/'gpu-execution.json')=={'exit':0,'stderr_bytes':0}
f=read(b/'full25/FINAL-SOURCE-FREEZE.json');assert all(sha(r/n)==v for n,v in f.items());src=read(o/'source.json');assert all(sha(Path(src['stage'])/n)==v for n,v in src['pins'].items())
(o/'POSTFLIGHT.json').write_text(json.dumps({'gpu_50_checks':True,'gpu_quiet':True,'stage_pins':True,'actual_current_root25_freeze':True,'runner_failure':'Final wrapper expected root24 freeze after authorized root25 adoption. GPU result complete and quiet. No GPU rerun; this independent postflight verifies actual current25 freeze instead.'},indent=2),encoding='utf-8')
o=b/'full25b';assert not o.exists();o.mkdir();backup=Path('C:/Project/game-research/implementation-backups/chapter1-before25b-20261103-01');assert not backup.exists();backup.mkdir()
for n in ['chapter1/chapter_one_view.gd','chapter1/ChapterOne.tscn','project.godot','export_presets.cfg']:
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/n,p)
(backup/'root25-freeze.json').write_text(json.dumps(f,indent=2),encoding='utf-8')
p=r/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8');assert s.count('chapter_actors_quality25_warm.gd')==1;p.write_text(s.replace('chapter_actors_quality25_warm.gd','chapter_actors_quality25b.gd'),encoding='utf-8')
s=(b/'full25/package_full25.py').read_text(encoding='utf-8').replace('candidate25','candidate25b').replace('20261103-25','20261103-25b').replace('Quality25','Quality25b').replace('chapter_actors_quality25_warm.gd','chapter_actors_quality25b.gd').replace('Full chapter candidate25:','Full chapter candidate25b: release-safe warm pool;')
(o/'package_full25b.py').write_text(s,encoding='utf-8');shutil.copy2(b/'full25/RUN.ko.md',o/'RUN.ko.md')
(o/'ADOPTION.json').write_text(json.dumps({'backup':str(backup),'preserved_exes':{str(p.relative_to(r)).replace('\\','/'):sha(p) for p in (r/'builds/chapter1').glob('chapter1-full-candidate-*/AshenCloister-Chapter1.exe')},'tested_source':{'chapter1/view/chapter_actors_quality25b.gd':sha(r/'chapter1/view/chapter_actors_quality25b.gd')},'proof':'pool25/fixed-fixture01 + POSTFLIGHT.json','prior_failure':'full25/FAILURE.ko.md','scope':'Development release fix, not final chapter quality approval.'},indent=2),encoding='utf-8')
