from pathlib import Path
import json,hashlib,importlib.util
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';OUT=B/'full17b/independent-audit01';assert not OUT.exists();OUT.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(B/'full17/FINAL-SOURCE-FREEZE.json');b=read(B/'full17b/FINAL-SOURCE-FREEZE.json');diff=[n for n in a if a[n]!=b[n]]
checks={'only_world_source_changed':diff==['chapter1/view/chapter_world_quality17.gd'],'world17_preserved':sha(B/'full17b/world17-before-boundary.gd')==a['chapter1/view/chapter_world_quality17.gd'],'root17b_freeze':all(sha(R/n)==h for n,h in b.items())}
for number in ['14','16','17','17b']:
 build=read(B/('full'+number+'/build/build.json'));checks['exe'+number+'_preserved']=sha(Path(build['exe']))==build['sha256']
 stage=Path(read(B/('full'+number+'/build/closure.json'))['stage']);pins=read(B/('full'+number+'/build/staging-manifest.json'));checks['stage'+number+'_preserved']=all(sha(stage/n)==h for n,h in pins.items())
boundary=read(B/'full17b/runtime/boundary01/RESULT.json');checks['outside_core_boundary']=boundary['all_stones_outside_walkable_plus_0_8'] and boundary['core_queries_unchanged']
spec=importlib.util.spec_from_file_location('pck17b',R/'tools/build_phase7.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);build=read(B/'full17b/build/build.json');audit=read(B/'full17b/build/pck-audit.json');checks['pck_reparse']=mod.pck_entries(Path(build['exe']))['entries']==audit['entries']
report={'checks':checks,'source_diff_vs17':diff,'boundary':boundary,'scope':'Decorative placement only. Does not claim a new full17b normalGPU run;17 fullGPU and17b edge fixture kept separate.'};(OUT/'RESULT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');assert all(checks.values());print(json.dumps({'checks':len(checks),'all':all(checks.values())}),flush=True)
