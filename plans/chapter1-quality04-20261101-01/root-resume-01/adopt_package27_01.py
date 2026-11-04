from pathlib import Path
import json,hashlib,shutil,re,subprocess,sys
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full27'
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(B/'hud27/fixture01/RESULT.json')['passed']
frozen=read(B/'full26/FINAL-SOURCE-FREEZE.json');assert all(sha(R/n)==h for n,h in frozen.items())
pins=read(B/'full26/ADOPTION.json')['preserved_exes'];build=read(B/'full26/build/build.json');pins[str(Path(build['exe']).relative_to(R)).replace('\\','/')]=build['sha256']
assert all(sha(R/n)==h for n,h in pins.items())
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before27-20261104-01');assert not backup.exists() and not O.exists();backup.mkdir();O.mkdir()
for n in ['chapter1/chapter_one_view.gd','project.godot','export_presets.cfg']:
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
shutil.copy2(B/'full26/FINAL-SOURCE-FREEZE.json',backup/'root26-freeze.json')
assembly=R/'chapter1/chapter_one_view.gd';s=assembly.read_text(encoding='utf-8');assert s.count('chapter_hud_quality23.gd')==1;s=s.replace('chapter_hud_quality23.gd','chapter_hud_quality27.gd');assembly.write_text(s,encoding='utf-8')
(O/'ADOPTION.json').write_text(json.dumps(dict(backup=str(backup),preserved_exes=pins,scope='Only HUD23->27 assembly change. World27 and Actor26 studies remain unconnected.'),indent=2),encoding='utf-8')
source=(B/'full26/package_full26.py').read_text(encoding='utf-8')
source=source.replace('chapter1-full-candidate-20261104-26','chapter1-full-candidate-20261104-27').replace('Quality26','Quality27').replace('candidate26 workflow','candidate27 workflow')
source=source.replace("'chapter1/view/chapter_elements_quality26.gd']","'chapter1/view/chapter_elements_quality26.gd','chapter1/view/chapter_hud_quality27.gd']")
source=source.replace('==123','==124')
scope='Full chapter candidate27: temporary combat notices stay below champion/boss health bars. Core16/World22/Actor25b/HUD27/Input21/FX26; unchanged drops and combat rules. Actor26 hit and World27 floor studies not adopted. Actual packaged/manual/audio/final performance approval separate.'
source=re.sub(r'^SCOPE=.*$', 'SCOPE='+repr(scope),source,flags=re.M)
source=source.replace('Only ground-item name presentation changed from25b. Prior full17 three-primary/full19 frost proofs retained for unchanged16 simulation only; no new full26 whole run claimed.','Only toast layout changed from26. Prior simulation results apply to unchanged core16 only; no new full27 whole run claimed.')
script=O/'package_full27.py';script.write_text(source,encoding='utf-8')
(O/'RUN.ko.md').write_text('# 후보27\n\nAshenCloister-Chapter1.exe를 실행합니다. 보스 체력 막대와 임시 알림의 겹침을 줄였습니다. 별도 Quality27 저장 경로를 사용하며 기존 사용자 저장은 변경하지 않습니다. 후보26 이하와 모든 연구·실패 기록은 보존합니다. 최종 품질 검수 중입니다.\n',encoding='utf-8')
subprocess.run([sys.executable,str(script),'freeze','--output',str(O/'FINAL-SOURCE-FREEZE.json')],check=True)
subprocess.run([sys.executable,str(script),'build','--freeze',str(O/'FINAL-SOURCE-FREEZE.json')],check=True)
assert all(sha(R/n)==h for n,h in pins.items())
print('CANDIDATE27 PACKAGE COMPLETE; ACTUAL GPU PENDING',flush=True)
