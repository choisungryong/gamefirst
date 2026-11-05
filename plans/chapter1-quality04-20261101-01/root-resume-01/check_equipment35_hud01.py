from pathlib import Path
import json,shutil,subprocess,hashlib
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'equipment35/hud01';S=Path('C:/Project/game-research/build-staging/chapter1-equipment35-hud01')
assert not O.exists() and not S.exists();O.mkdir(parents=True);S.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=Path(read(B/'full34/build/closure.json')['stage'])
for n,h in read(B/'full34/build/staging-manifest.json').items():
 assert sha(old/n)==h
 p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/n,p)
for n in ['chapter1/view/equipment_sigil_quality35.gd','chapter1/view/chapter_hud_quality35.gd']+[str(p.relative_to(R)) for p in (R/'chapter1/art/equipment_icons35').glob('*.svg')]:
 p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
(S/'check35.gd').write_text('extends SceneTree\nfunc _initialize() -> void:\n var hud=load("res://chapter1/view/chapter_hud_quality35.gd").new()\n for slot in ["weapon","body","ring","charm"]:\n  var icon=hud._sigil({"slot":slot,"quality":"rare"})\n  assert(icon.custom_minimum_size==Vector2(56,56))\n  assert(icon.PAINTINGS[slot].get_width()>0)\n  icon.free()\n hud.free()\n quit()\n',encoding='utf-8')
pins={str(p.relative_to(S)):sha(p) for p in S.rglob('*') if p.is_file()};(O/'SOURCE.json').write_text(json.dumps({'stage':str(S),'pins':pins},indent=2),encoding='utf-8')
engine='C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe'
for label,args in [('import',['--headless','--editor','--import']),('check',['--headless','--script','res://check35.gd'])]:
 with (O/(label+'.stdout.txt')).open('xb') as out,(O/(label+'.stderr.txt')).open('xb') as err:
  cmd=[engine,'--path',str(S)]+args;p=subprocess.Popen(cmd,stdout=out,stderr=err);(O/(label+'-launch.json')).write_text(json.dumps({'pid':p.pid,'command':cmd}));code=p.wait(timeout=180)
 result={'exit':code,'stderr_bytes':(O/(label+'.stderr.txt')).stat().st_size};(O/(label+'-execution.json')).write_text(json.dumps(result));print(label,result,flush=True);assert result=={'exit':0,'stderr_bytes':0}
(O/'STATUS.ko.md').write_text('HUD35 미연결 소스 import 및 네 슬롯 생성 검사 통과. 실제 발견·보상·인벤토리 화면 배치 검수는 아직 미완료. 제품34 assembly와 저장 변경 없음.',encoding='utf-8')
