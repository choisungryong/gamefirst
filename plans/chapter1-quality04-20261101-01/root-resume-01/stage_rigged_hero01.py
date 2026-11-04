from pathlib import Path
import json,shutil,hashlib,subprocess
ROOT=Path('C:/Project/d2r-combat-baseline');HERE=Path(__file__).parent
OUT=HERE.parent/'rigged-hero-01';STAGE=Path('C:/Project/game-research/build-staging/rigged-hero-20261101-01')
assert not OUT.exists() and not STAGE.exists();OUT.mkdir();STAGE.mkdir()
source=Path('C:/Project/game-research/art-sources/oga-mage-20261101-01/gltf-preview-06/mage_animated.glb')
model=ROOT/'chapter1/art/rigged_mage/v01/mage_animated.glb';assert not model.exists();model.parent.mkdir(parents=True)
shutil.copy2(source,model)
(model.parent/'.gdignore').write_text('',encoding='utf-8')
(model.parent/'ATTRIBUTION.ko.md').write_text('''# 리깅 mage 연구 후보

원작: thecubber, Rigged textured mage. 원 리그 크레딧 Julius / OpenGameArt.
출처: https://opengameart.org/content/rigged-textured-mage
라이선스: CC BY-SA3.0 https://creativecommons.org/licenses/by-sa/3.0/

변경: 구형 재질 변환, 자체 IK 보행/대기/시전/피격/사망과 베이크, 무가중치 정점2053 보정과4가중치 정규화, 미터 변환. 이 파생 모델/렌더는 같은 CC BY-SA3.0을 따릅니다. 원본 및 파생 .blend는 로컬 연구 source 디렉터리에 보존했습니다. 원작D2/SACRATA 자산을 사용하지 않습니다. 아직 비교 중인 후보이며 기본09 실행은 교체하지 않았습니다.
''',encoding='utf-8')
closure=json.loads((HERE.parent/'full09/build/closure.json').read_text(encoding='utf-8'))['runtime_source_files']
extras=['chapter1/view/rigged_hero_actors.gd','chapter1/view/rigged_hero_occlusion.gdshader',str(model.relative_to(ROOT)).replace('\\','/')]
pins={}
for name in closure+extras:
 dest=STAGE/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dest);pins[name]=hashlib.sha256(dest.read_bytes()).hexdigest()
oldstage=Path('C:/Project/game-research/build-staging/chapter1-full-candidate-20261101-09')
project=(oldstage/'project.godot').read_text(encoding='utf-8').replace('Ashen Cloister ChapterOne Quality09','Rigged Hero Research').replace('AshenCloisterChapterOneQuality09','AshenCloisterChapterOneRigResearch')
(STAGE/'project.godot').write_text(project,encoding='utf-8')
p=STAGE/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8');s=s.replace('res://chapter1/view/chapter_actors.gd','res://chapter1/view/rigged_hero_actors.gd');p.write_text(s,encoding='utf-8')
# One actual model casts a real shadow in this research scene.
p=STAGE/'chapter1/view/cloister_world_quality03.gd';s=p.read_text(encoding='utf-8').replace('moon.shadow_enabled=false','moon.shadow_enabled=true');p.write_text(s,encoding='utf-8')
with (OUT/'stage-manifest.json').open('x',encoding='utf-8') as f:json.dump({'source_pins_before_stage_injections':pins,'stage_changes':['chapter_one_view presenter preload','world moon shadows enabled'],'stage':str(STAGE),'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'scope':'Research only. Existing09 EXE/core/profile unchanged.'},f,indent=2)
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
command=[engine,'--headless','--path',str(STAGE),'--editor','--import']
r=subprocess.run(command,capture_output=True,timeout=180)
with (OUT/'import-execution.json').open('x',encoding='utf-8') as f:json.dump({'command':command,'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace')},f,indent=2)
print(json.dumps({'actual_exit':r.returncode,'stderr':r.stderr.decode('utf-8','replace')}))
