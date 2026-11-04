from pathlib import Path
import json,hashlib,shutil,re,subprocess,sys
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full28'
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(B/'actor28/mapped02/COMPARISON.json')['passed'] and read(B/'actor28/mapped02/FACING-AUDIT01.json')['passed']
assert all(read(B/'actor28/fixture02/RESULT.json')['checks'].values())
frozen=read(B/'full27/FINAL-SOURCE-FREEZE.json');assert all(sha(R/n)==h for n,h in frozen.items())
pins=read(B/'full27/ADOPTION.json')['preserved_exes'];build=read(B/'full27/build/build.json');pins[str(Path(build['exe']).relative_to(R)).replace('\\','/')]=build['sha256'];assert all(sha(R/n)==h for n,h in pins.items())
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before28-20261104-01');assert not backup.exists() and not O.exists();backup.mkdir();O.mkdir()
for n in ['chapter1/chapter_one_view.gd','project.godot','export_presets.cfg']:
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
shutil.copy2(B/'full27/FINAL-SOURCE-FREEZE.json',backup/'root27-freeze.json')
assembly=R/'chapter1/chapter_one_view.gd';s=assembly.read_text(encoding='utf-8');assert s.count('chapter_actors_quality25b.gd')==1;assembly.write_text(s.replace('chapter_actors_quality25b.gd','chapter_actors_quality28.gd'),encoding='utf-8')
(O/'ADOPTION.json').write_text(json.dumps(dict(backup=str(backup),preserved_exes=pins,scope='Only Actor25b->28 assembly and Actor28 dependency addition. HUD27 and World22 retained; World27 floor study unconnected. Failed first fixture and movie assumptions preserved.'),indent=2),encoding='utf-8')
source=(B/'full27/package_full27.py').read_text(encoding='utf-8').replace('chapter1-full-candidate-20261104-27','chapter1-full-candidate-20261104-28').replace('Quality27','Quality28').replace('candidate27 workflow','candidate28 workflow')
source=source.replace("'chapter1/view/chapter_hud_quality27.gd']","'chapter1/view/chapter_hud_quality27.gd','chapter1/view/chapter_actors_quality28.gd']").replace('==124','==125')
scope='Full chapter candidate28: readable upper-body hit recoil, planted lower-body poses, and paid attack direction retained during recovery. Core16/World22/Actor28/HUD27/Input21/FX26; combat rules unchanged. World27 floor study not adopted. Actual package/manual/audio/final performance gates separate.'
source=re.sub(r'^SCOPE=.*$','SCOPE='+repr(scope),source,flags=re.M)
source=source.replace('Only toast layout changed from26. Prior simulation results apply to unchanged core16 only; no new full27 whole run claimed.','Only actor presentation changed from27. Prior simulation results apply to unchanged core16 only; no new full28 whole run claimed.')
script=O/'package_full28.py';script.write_text(source,encoding='utf-8')
(O/'RUN.ko.md').write_text('# 후보28\n\nAshenCloister-Chapter1.exe를 실행합니다. 상체 피격 반동과 공격 회복 방향을 개선했습니다. Quality28 별도 저장 경로이며 기존 저장은 변경하지 않습니다. 이전 후보·실패 증거는 보존했습니다. 최종 품질 검수 중입니다.\n',encoding='utf-8')
subprocess.run([sys.executable,str(script),'freeze','--output',str(O/'FINAL-SOURCE-FREEZE.json')],check=True)
subprocess.run([sys.executable,str(script),'build','--freeze',str(O/'FINAL-SOURCE-FREEZE.json')],check=True)
assert all(sha(R/n)==h for n,h in pins.items());print('CANDIDATE28 PACKAGE COMPLETE; ACTUAL GPU PENDING',flush=True)
