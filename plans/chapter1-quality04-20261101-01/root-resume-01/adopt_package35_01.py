from pathlib import Path
import json,hashlib,shutil,re,subprocess,sys
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full35';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'))
assert not O.exists()
assert all(sha(R/n)==h for n,h in read(B/'full34/FINAL-SOURCE-FREEZE.json').items())
for scope in ['layout01','slots01']:
 for label in ['import','check','gpu']:assert read(B/f'equipment35/{scope}/{label}-execution.json')=={'exit':0,'stderr_bytes':0}
 assert read(B/f'equipment35/{scope}/RESULT.json')['core_unchanged']
for n in ['chapter1/view/equipment_sigil_quality35.gd','chapter1/view/chapter_hud_quality35.gd']:
 assert sha(R/n)==read(B/'equipment35/slots01/SOURCE.json')['pins'][n.replace('/',chr(92))]
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before35-20261106-01');assert not backup.exists();backup.mkdir();O.mkdir()
a=read(B/'full34/ADOPTION.json');pins=a['preserved_exes'];build=read(B/'full34/build/build.json');pins[str(Path(build['exe']).relative_to(R)).replace(chr(92),'/')]=build['sha256']
assert all(sha(R/n)==h for n,h in pins.items());users=a['user_pins'];assert all(sha(Path(n))==h for n,h in users.items())
for n in ['chapter1/chapter_one_view.gd','project.godot','export_presets.cfg']:
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
shutil.copy2(B/'full34/FINAL-SOURCE-FREEZE.json',backup/'root34-freeze.json')
for n in users:
 p=Path(n);dest=backup/'user-profiles'/p.parent.name/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
p=R/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8');assert s.count('chapter_hud_quality27.gd')==1;p.write_text(s.replace('chapter_hud_quality27.gd','chapter_hud_quality35.gd'),encoding='utf-8')
(O/'ADOPTION.json').write_text(json.dumps({'backup':str(backup),'preserved_exes':pins,'user_pins':users,'scope':'HUD35 painted slot icons only. Core16/World31d/Actor34b/Input21/FX33b retained. All final gates remain scoped.'},indent=2),encoding='utf-8')
s=(B/'full34/package_full34.py').read_text(encoding='utf-8').replace('chapter1-full-candidate-20261105-34','chapter1-full-candidate-20261106-35').replace('Quality34','Quality35').replace('candidate34 workflow','candidate35 workflow').replace('==141','==149')
extras=['chapter1/view/equipment_sigil_quality35.gd','chapter1/view/chapter_hud_quality35.gd']+[f'chapter1/art/equipment_icons35/{n}' for n in ['weapon.svg','body.svg','ring.svg','charm.svg','ATTRIBUTION.ko.md','MANIFEST.json']]
pos=s.index('\ndef paths():');s=s[:pos]+'\nEXTRAS += '+repr(extras)+'\n'+s[pos:]
s=s.replace("'.png','.wav','.glb'","'.png','.wav','.glb','.svg'")
s=s.replace('chapter1/art/skeleton_outlaw/v02/*.json"','chapter1/art/skeleton_outlaw/v02/*.json,chapter1/art/equipment_icons35/*.md,chapter1/art/equipment_icons35/*.json"')
s=re.sub(r'^SCOPE=.*$',"SCOPE="+repr('Candidate35: Core16/World31d/Actor34b/HUD35/Input21/FX33b. Four original painted equipment slot SVGs replace minimal sigils in discovery/reward/comparison. Combat, loot, growth and save rules retained. Source layout/core/scroll checks passed; actual package GPU/manual/hearing/final performance remain separate.'),s,flags=re.M)
s=s.replace('Only walker family presentation changed from33. Prior core16 results retain their scope; no new full34 whole run claimed.','Only equipment icon presentation changed from34. Prior whole runs retain their scope; no new full35 whole run claimed.')
s=s.replace("shutil.copy2(HERE/'RUN.ko.md',OUTPUT/'RUN.ko.md')","shutil.copy2(ROOT/'chapter1/art/equipment_icons35/ATTRIBUTION.ko.md',credits/'ATTRIBUTION-Equipment-Icons35.ko.md')\n    shutil.copy2(ROOT/'chapter1/art/equipment_icons35/MANIFEST.json',credits/'Equipment-Icons35-MANIFEST.json')\n    shutil.copy2(HERE/'RUN.ko.md',OUTPUT/'RUN.ko.md')")
p=O/'package_full35.py';p.write_text(s,encoding='utf-8');(O/'RUN.ko.md').write_text('# 후보35\n\n장비 발견·보스 보상·장비 비교의 네 슬롯 그림을 개선한 후보입니다. 별도 Quality35 저장 경로. 이전 후보와 사용자 저장은 보존합니다. 최종 품질 검수 중입니다.\n',encoding='utf-8')
subprocess.run([sys.executable,str(p),'freeze','--output',str(O/'FINAL-SOURCE-FREEZE.json')],check=True)
subprocess.run([sys.executable,str(p),'build','--freeze',str(O/'FINAL-SOURCE-FREEZE.json')],check=True)
assert all(sha(R/n)==h for n,h in pins.items());assert all(sha(Path(n))==h for n,h in users.items());print('PACKAGE35 COMPLETE',flush=True)
