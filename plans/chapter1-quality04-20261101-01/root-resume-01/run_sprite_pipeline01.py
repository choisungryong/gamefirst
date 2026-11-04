from pathlib import Path
import importlib.util,json,hashlib,copy,shutil,subprocess
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'sprite-pipeline01';assert not O.exists();O.mkdir();sp=importlib.util.spec_from_file_location('spritecompiler',R/'tools/sprite_pipeline/compile.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks={};catalog=[]
for role in m.ROLES:
 ident=role+'-demo';dest=O/'assets'/ident;manifest=m.legacy(R/f'chapter1/art/actors/{role}.json',dest,ident,'res://'+str(dest.relative_to(R)).replace('\\','/'));catalog.append(dict(label={'hero':'주인공','walker':'일반 적','ranged':'원거리 적','charger':'돌진 적','elite':'정예'}[role]+' · 보존 스프라이트',actor='../assets/'+ident+'/actor.json'))
 original=read(R/f'chapter1/art/actors/{role}.json');compiled=read(dest/'actor.json');checks[role+'_anchors_exact']=[f['feet'] for f in original['frames']]==[f['feet'] for f in compiled['frames']];checks[role+'_regions_exact']=[f['region'] for f in original['frames']]==[f['region'] for f in compiled['frames']];checks[role+'_png_bytes_exact']=all(sha(dest/t['file'])==t['sha256'] for t in manifest['textures'].values())
work=O/'workbench';shutil.copytree(R/'tools/sprite_pipeline',work,ignore=shutil.ignore_patterns('__pycache__','*.py'));(work/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
base=read(R/'chapter1/art/actors/walker.json');keys={base['texture']}|{f.get('texture',base['texture']) for f in base['frames']};sources={k:R/k[6:] for k in keys};bad=[]
for name,alter in [('missing-direction',lambda d:d['frames_by_direction'].pop('west')),('out-of-range',lambda d:d['states']['cast'].append(99999)),('invalid-duration',lambda d:d['frames'][0].update(duration=0)),('out-of-bounds',lambda d:d['frames'][0].update(region=[0,0,99999,1]))]:
 d=copy.deepcopy(base);alter(d);target=O/('reject-'+name)
 try:m.compile_asset(d,sources,target,'bad-demo','res://not-installed/bad-demo');bad.append(name)
 except ValueError:checks[name+'_rejected_before_output']=not target.exists()
checks['no_invalid_input_accepted']=not bad
try:m.legacy(R/'chapter1/art/actors/walker.json',O/'assets/walker-demo','walker-demo','res://not-installed');checks['no_overwrite']=False
except ValueError:checks['no_overwrite']=True
checks['product30_frozen']=all(sha(R/n)==h for n,h in read(B/'full30/FINAL-SOURCE-FREEZE.json').items());assert all(checks.values()),checks
(O/'COMPILER-RESULT.json').write_text(json.dumps(dict(checks=checks,passed=True,scope='Five existing independently-authored sprite sheets, exact regions/anchors/PNG bytes, four invalid inputs rejected before output, refusal to overwrite and frozen product30 preserved.'),indent=2));print('SPRITE COMPILER',len(checks),'CHECKS PASS')
