from pathlib import Path
import hashlib,json,shutil,subprocess
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';HERE=Path(__file__).parent
AFTER=Path('C:/Project/game-research/build-staging/chapter1-elements-20261101-02');BEFORE=Path('C:/Project/game-research/build-staging/chapter1-elements-before13-20261101-02');OUT=BASE/'elements14/arena02'
assert not OUT.exists()and not BEFORE.exists();OUT.mkdir();BEFORE.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=Path('C:/Project/game-research/build-staging/chapter1-full-candidate-20261101-13');pins=json.loads((BASE/'full13/build/staging-manifest.json').read_text(encoding='utf-8'))
for name,h in pins.items():
 assert sha(old/name)==h
 target=BEFORE/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/name,target)
for stage,variant in [(AFTER,'after14'),(BEFORE,'before13')]:
 shutil.copy2(HERE/'elements_fixture14.gd',stage/'elements_fixture.gd')
 (stage/'ElementsFixture.tscn').write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://elements_fixture.gd" id="1"]\n[node name="ElementsFixture" type="Node3D"]\nscript=ExtResource("1")\n',encoding='utf-8')
 p=stage/'project.godot';s=p.read_text(encoding='utf-8')
 if variant=='before13':s=s.replace('Quality13','Elements13BeforeArena02')
 p.write_text(s,encoding='utf-8')
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for stage,variant in [(AFTER,'after14'),(BEFORE,'before13')]:
 proof=OUT/variant;proof.mkdir()
 for label,args in [('import',['--headless','--editor','--import']),('check',['--headless','--check-only','--script','res://elements_fixture.gd']),('gpu',['--fixed-fps','60','res://ElementsFixture.tscn','--','--chapter1-profile-off','--chapter1-start','--chapter1-qa-ignore-focus','--chapter1-quit-after=14','--elements-variant='+variant])]:
  command=[engine,'--path',str(stage)]+args
  with(proof/(label+'.stdout.txt')).open('xb')as stdout,(proof/(label+'.stderr.txt')).open('xb')as stderr:
   p=subprocess.Popen(command,stdout=stdout,stderr=stderr)
   (proof/(label+'-launch.json')).write_text(json.dumps({'pid':p.pid,'command':command},indent=2),encoding='utf-8');print(json.dumps({'variant':variant,'label':label,'pid':p.pid}),flush=True)
   code=p.wait(timeout=160)
  report={'actual_exit':code,'stderr_bytes':(proof/(label+'.stderr.txt')).stat().st_size};(proof/(label+'-execution.json')).write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report),flush=True)
  if code!=0 or report['stderr_bytes']:raise RuntimeError((variant,label))
 shutil.copy2(stage/'elements-result.json',proof/'result.json');shutil.copytree(stage/'fixture-captures',proof/'captures')
a=json.loads((OUT/'after14/result.json').read_text(encoding='utf-8'));b=json.loads((OUT/'before13/result.json').read_text(encoding='utf-8'))
same={k:a[k]==b[k]for k in ['tick','kills','counts','max_frozen','metrics','hero','growth']};assert all(same.values()),same
assert a['counts']['shatter']>0 and a['max_frozen']>0 and a['counts']['arc_casts']>0,a
(OUT/'COMPARISON.json').write_text(json.dumps({'same_core_arena':same,'after':a,'scope':'Actual core events in declared configured arena, fixed60 GPU captures. Not normal full chapter/manual/performance or final art approval.'},indent=2),encoding='utf-8');print(json.dumps({'same':same,'counts':a['counts'],'max_frozen':a['max_frozen']}),flush=True)
