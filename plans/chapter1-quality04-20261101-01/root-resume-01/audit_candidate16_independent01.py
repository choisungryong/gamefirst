from pathlib import Path
import json,hashlib,importlib.util
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'full16/independent-audit01';assert not OUT.exists();OUT.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=read(BASE/'full16/FINAL-SOURCE-FREEZE.json');closure=read(BASE/'full16/build/closure.json');stage=Path(closure['stage']);stagepins=read(BASE/'full16/build/staging-manifest.json')
checks={}
checks['root16_freeze_matches']=all(sha(ROOT/n)==h for n,h in freeze.items())
checks['stage16_matches']=all(sha(stage/n)==h for n,h in stagepins.items())
actor='chapter1/view/chapter_actors_quality16.gd'
tested=read(BASE/'cold16/actors01/after-source.json')['pins'][actor]
checks['packaged_actor_is_gpu_tested_source']=freeze[actor]==stagepins[actor]==tested
checks['four16_sources_in_closure']=all(n in closure['runtime_source_files'] for n in [actor,'chapter1/core/chapter_run_quality16.gd','chapter1/view/chapter_elements_quality16.gd','chapter1/view/chapter_hud_quality16.gd'])
oldstage=Path('C:/Project/game-research/build-staging/chapter1-full-candidate-20261101-14')
oldpins=read(BASE/'full14/build/staging-manifest.json')
checks['archived14_stage_unchanged']=all(sha(oldstage/n)==h for n,h in oldpins.items())
oldexe=ROOT/'builds/chapter1/chapter1-full-candidate-20261101-14/AshenCloister-Chapter1.exe'
checks['candidate14_exe_unchanged']=sha(oldexe)=='5fa58077545ea3cc3c0d55bc6abbd5bc57eab32bdd78c8ccdbfa398ca28f5952'
exe=Path(closure['output'])/'AshenCloister-Chapter1.exe'
spec=importlib.util.spec_from_file_location('pck_parser',ROOT/'tools/build_phase7.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
pck=parser.pck_entries(exe);recorded=read(BASE/'full16/build/pck-audit.json')
checks['actual_exe_matches_packaging_audit']=sha(exe)==recorded['exe_sha256'] and pck['entries']==recorded['entries']
entries={e['path'].removeprefix('res://'):e for e in pck['entries']}
checks['four16_scripts_present']=all(n+'.remap' in entries for n in [actor,'chapter1/core/chapter_run_quality16.gd','chapter1/view/chapter_elements_quality16.gd','chapter1/view/chapter_hud_quality16.gd'])
checks['no_evidence_tests_research_in_pck']=not any(n.startswith(('plans/','tests/','evidence/','research/')) for n in entries)
proofs={}
for name,key in [('full-release-proof.json','result'),('full-frost-proof.json','first_victory'),('full-arc-proof.json','first_victory')]:
 p=BASE/'full16/build'/name
 if p.exists():
  row=read(p)[key];proofs[name]={k:row[k] for k in ['mode','tick','kills']};proofs[name]['seconds']=row['tick']/60
report={'checks':checks,'exe16_sha256':sha(exe),'runtime_sources':len(closure['runtime_source_files']),'stage_files':len(stagepins),'pck_entries':len(entries),'observed_headless_proofs':proofs,'scope':'Independent read-only pin/closure/PCK reparse audit while another chat owns package/full-GPU/movie work. Not full GPU/manual/audio/performance approval.'}
(OUT/'RESULT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False),flush=True)
assert all(checks.values())
