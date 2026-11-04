from pathlib import Path
import hashlib,json,subprocess,time,re
ROOT=Path('C:/Project/d2r-combat-baseline')
OUT=Path(__file__).resolve().parent
GODOT=Path('C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
 p=OUT/name
 assert not p.exists(),p
 p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def copy_fixture(source,name):
 text=(ROOT/source).read_text(encoding='utf-8')
 # Only pilot accepts an output argument. Every other copied fixture is stdout-only.
 if name!='normal-pilot.gd':assert 'FileAccess.WRITE' not in text and 'store_string' not in text
 target=OUT/name;assert not target.exists();target.write_text(text,encoding='utf-8')
 return {'source':source,'source_sha256':sha(ROOT/source),'copy':target.relative_to(ROOT).as_posix(),'copy_sha256':sha(target),'output_rewire':'stdout-only; no historic file writes' if name!='normal-pilot.gd' else 'explicit --output under verification-01 at execution'}
def pins():
 product=['chapter1/core/combat_run.gd','chapter1/core/run_growth.gd','chapter1/core/growth_catalog.gd','chapter1/data/growth.json','combat/combat_resolver.gd','combat/stat_block.gd','chapter1/view/cloister_actors.gd','chapter1/view/cloister_effects.gd','chapter1/view/hero_occlusion_rim.gdshader','chapter1/presentation/combat_audio.gd','chapter1/presentation/frame_probe.gd','chapter1/chapter_view.gd']
 historical=[]
 for directory in ['chapter1/evidence/core-pilot-20261031-03','plans/chapter1-c2-20261031-01/verification-core-03','plans/chapter1-quality-20261031-01/verification-01','plans/chapter1-quality-20261031-01/verification-02']:
  historical.extend(p for p in (ROOT/directory).rglob('*') if p.is_file())
 backup=Path('C:/Project/game-research/implementation-backups/chapter1-quality04-before-20261101-01')
 bm=json.loads((backup/'manifest.json').read_text(encoding='utf-8'))
 historical.extend((backup/'source'/p) for p in bm['files'])
 historical.extend(ROOT/p for p in bm['pinned_exes3_profiles2'])
 historical.append(backup/'manifest.json')
 return {'product':{p:sha(ROOT/p) for p in product},'historical_selected':{str(p):sha(p) for p in sorted(set(historical))}}
def execute(label,script=None,args=None,expected=0):
 command=[str(GODOT),'--headless','--path',str(ROOT)]
 command+=['--script','res://'+(OUT/script).relative_to(ROOT).as_posix()] if script else []
 command+=args or []
 begin=time.monotonic();r=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=240)
 record={'command':command,'actual_exit':r.returncode,'expected_exit':expected,'wall_seconds':time.monotonic()-begin,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace'),'source_pins':pins()['product']}
 write(label+'-execution.json',record)
 print(label,'actual',r.returncode,'stderr',len(r.stderr),flush=True)
 return record
def main():
 before=pins();write('pins-before.json',before)
 copied=[]
 for source,name in [('core04/semantic_regression.gd','semantic.gd'),('core04/test_crowd.gd','crowd.gd'),('core04/normal_pilot.gd','normal-pilot.gd'),('presentation/contract.gd','presentation.gd'),('measurement/test_frame_probe.gd','probe.gd')]:
  copied.append(copy_fixture('plans/chapter1-quality04-20261101-01/'+source,name))
 write('fixture-provenance.json',copied)
 records=[]
 for label,script in [('semantic','semantic.gd'),('crowd','crowd.gd'),('presentation','presentation.gd'),('probe','probe.gd'),('independent-core','independent-core.gd')]:
  records.append(execute(label,script))
  records.append(execute(label+'-negative',script,['--','--prove-failure'],1) if label!='probe' else execute('scene-check',None,['--check-only','--script','res://chapter1/chapter_view.gd']))
 records.append(execute('normal-pilot','normal-pilot.gd',['--','--output='+str(OUT/'normal-results.json')],None))
 after=pins();write('pins-after.json',after)
 write('execution-summary.json',{'expected_exit_checks':all(r['expected_exit'] is None or r['actual_exit']==r['expected_exit'] for r in records),'stderr_empty':all(not r['stderr'] for r in records),'source_unchanged':before['product']==after['product'],'historical_selected_unchanged':before['historical_selected']==after['historical_selected'],'historical_selected_count':len(before['historical_selected']),'scope':'CPU/headless independent verification, copied owner fixtures and new rotated queue fixtures. No GPU, normal balance, quality or listening approval.'})
if __name__=='__main__':main()
