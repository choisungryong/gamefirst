from pathlib import Path
import json,shutil,subprocess,hashlib
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01'
OUT=BASE/'boss-research12';STAGE=Path('C:/Project/game-research/build-staging/chapter1-warden-research-20261101-01')
assert not OUT.exists()and not STAGE.exists();OUT.mkdir();STAGE.mkdir()
model=ROOT/'chapter1/art/chained_warden/v01/chained_demon_animated.glb';assert not model.exists();model.parent.mkdir(parents=True)
source=Path('C:/Project/game-research/art-sources/oga-chained-demon-20261101-01/motion-04/chained_demon_animated.glb')
shutil.copy2(source,model);(model.parent/'.gdignore').write_text('',encoding='utf-8')
(model.parent/'ATTRIBUTION.ko.md').write_text('''# 사슬 파수왕 연구 모델

원 모델: Mophs, Chained Demon, https://opengameart.org/content/chained-demon .
제공된 대안 중 CC BY3.0을 선택합니다: https://creativecommons.org/licenses/by/3.0/ .
변경: 구형 재질의 PBR 변환/packed diffuse, smooth shading, 초과 정점 가중치4개 검증/보정,
새 RootMotion, 자체 FK 대기/보행/두 전조/내려치기/부채/피격/사망8클립, 미터 변환.
원본/파생 source는 C:/Project/game-research/art-sources/oga-chained-demon-20261101-01/에 보존했습니다.
원작D2/SACRATA 자산을 사용하지 않습니다. 아직 외형/타이밍 검수 중이며 후보11 실행본은 변경하지 않았습니다.
''',encoding='utf-8')
freeze=json.loads((BASE/'full11/FINAL-SOURCE-FREEZE.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert all(sha(ROOT/n)==h for n,h in freeze.items())
names=json.loads((BASE/'full11/build/closure.json').read_text(encoding='utf-8'))['runtime_source_files']+['chapter1/view/chapter_actors_quality12.gd',str(model.relative_to(ROOT)).replace('\\','/'),'chapter1/art/chained_warden/v01/ATTRIBUTION.ko.md']
for name in names:
 p=STAGE/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,p)
shutil.copy2(Path('C:/Project/game-research/build-staging/chapter1-full-candidate-20261101-11/project.godot'),STAGE/'project.godot')
p=STAGE/'chapter1/chapter_one_view.gd';p.write_text(p.read_text(encoding='utf-8').replace('res://chapter1/view/rigged_hero_actors.gd','res://chapter1/view/chapter_actors_quality12.gd'),encoding='utf-8')
shutil.copy2(Path(__file__).with_name('warden_fixture12.gd'),STAGE/'warden_fixture.gd')
(STAGE/'WardenFixture.tscn').write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://warden_fixture.gd" id="1"]\n[node name="WardenFixture" type="Node3D"]\nscript=ExtResource("1")\n',encoding='utf-8')
with(OUT/'stage-manifest.json').open('x',encoding='utf-8')as f:json.dump({'stage':str(STAGE),'runtime_pins':{str(p.relative_to(STAGE)).replace('\\','/'):sha(p)for p in STAGE.rglob('*')if p.is_file()},'chapter11_freeze_matches':True,'scope':'Only staged presenter preload differs. No runtime11/core/profile modification; fixture is explicit synthetic placement.'},f,indent=2)
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
proof=OUT/'fixture01';proof.mkdir()
for label,args in [('import',['--headless','--editor','--import']),('fixture',['res://WardenFixture.tscn','--max-fps','120','--','--chapter1-profile-off','--chapter1-start','--chapter1-qa-ignore-focus','--chapter1-quit-after=12.3'])]:
 command=[engine,'--path',str(STAGE)]+args;r=subprocess.run(command,capture_output=True,timeout=180)
 with(proof/(label+'-execution.json')).open('x',encoding='utf-8')as f:json.dump({'command':command,'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace')},f,indent=2)
 print(json.dumps({'label':label,'actual_exit':r.returncode,'stderr':r.stderr.decode('utf-8','replace')[:2000]}),flush=True)
 if r.returncode!=0 or r.stderr:raise RuntimeError(label)
capture=STAGE/'plans/chapter1-quality04-20261101-01/boss-research12/fixture01/captures'
if capture.exists():shutil.copytree(capture,proof/'captures')
