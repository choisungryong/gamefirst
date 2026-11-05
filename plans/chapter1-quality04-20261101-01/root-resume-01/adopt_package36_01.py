from pathlib import Path
import json,hashlib,shutil,re,subprocess,sys
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full36';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not O.exists();assert all(sha(R/n)==h for n,h in read(B/'full35/FINAL-SOURCE-FREEZE.json').items())
for p in ['balance36/rules02/RESULT.json','balance36/normal01/RESULT.json','balance36/normal02/RESULT.json','balance36/loot01/RESULT.json','balance36/growth01/RESULT.json','balance36/crowd02/RESULT.json','balance36/arc02/RESULT.json','balance36/arc-segments01/equivalence01/RESULT.json']:assert read(B/p)['passed'],p
assert all(r['core_equal'] for r in read(B/'balance36/cost01/COMPARISON.json')['runs'])
extras=['chapter1/core/combat_run_stun36.gd','chapter1/core/chapter_run_stun36.gd','chapter1/core/chapter_run_quality36.gd','chapter1/data/growth_quality36.json','chapter1/view/chapter_actors_quality36.gd','chapter1/view/chapter_elements_quality36.gd','chapter1/view/chapter_hud_quality36.gd']
study=read(B/'balance36/arc02/SOURCE.json');assert all(sha(R/n)==study['pins'][n.replace('/',chr(92))] for n in extras)
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before36-20261106-01');assert not backup.exists();backup.mkdir();O.mkdir()
a=read(B/'full35/ADOPTION.json');pins=a['preserved_exes'];old=read(B/'full35/build/build.json');pins[str(Path(old['exe']).relative_to(R)).replace(chr(92),'/')]=old['sha256'];users=a['user_pins'];assert all(sha(R/n)==h for n,h in pins.items());assert all(sha(Path(n))==h for n,h in users.items())
for n in ['chapter1/chapter_one_view.gd','project.godot','export_presets.cfg']:
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
shutil.copy2(B/'full35/FINAL-SOURCE-FREEZE.json',backup/'root35-freeze.json')
for n in users:
 p=Path(n);d=backup/'user-profiles'/p.parent.name/p.name;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)
p=R/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8')
for before,after in [('chapter_run_quality16.gd','chapter_run_quality36.gd'),('chapter_actors_quality34b.gd','chapter_actors_quality36.gd'),('chapter_elements_quality33b.gd','chapter_elements_quality36.gd'),('chapter_hud_quality35.gd','chapter_hud_quality36.gd')]:
 assert s.count(before)==1;s=s.replace(before,after)
p.write_text(s,encoding='utf-8')
(O/'ADOPTION.json').write_text(json.dumps({'backup':str(backup),'preserved_exes':pins,'user_pins':users,'tested_source':{n:sha(R/n) for n in extras},'scope':'Core36 elemental progression/shock/world uniques, Actor36 pose hold, FX36 true branch paths/shock cues, HUD36 growth explanations. World31d/Input21 retained. Existing sources/exes/saves preserved. Final quality gates open.'},indent=2),encoding='utf-8')
s=(B/'full35/package_full35.py').read_text(encoding='utf-8').replace('chapter1-full-candidate-20261106-35','chapter1-full-candidate-20261106-36').replace('Quality35','Quality36').replace('candidate35 workflow','candidate36 workflow').replace('==149','==156')
pos=s.index('\ndef paths():');s=s[:pos]+'\nEXTRAS += '+repr(extras)+'\n'+s[pos:]
s=re.sub(r'^SCOPE=.*$',"SCOPE="+repr('Candidate36: Core36/World31d/Actor36/HUD36/Input21/FX36. Progressive elemental propagation, separate brief arc stun and immunity, bounded probabilistic world uniques. True branch endpoint rendering and growth explanations. Source rules/multi-seed pacing/loot/GPU/cost evidence scoped; actual package whole/manual/hearing/final focused performance remain separate.'),s,flags=re.M)
s=s.replace('Only equipment icon presentation changed from34. Prior whole runs retain their scope; no new full35 whole run claimed.','Core36 changes combat and loot rules. Old Core16 whole runs are historical, not candidate36 outcome predictions. New source36 normal-policy evidence is separate from actual package verification.')
s=s.replace("root-resume-01/release_behavior_probe.gd","root-resume-01/release_behavior36_probe.gd")
p=O/'package_full36.py';p.write_text(s,encoding='utf-8');(O/'RUN.ko.md').write_text('# 후보36\n\n화염 폭발 전파·냉기 제어/파쇄·번개 연쇄/짧은 스턴과 확률 고유 장비를 반영한 검수 후보입니다. 별도 Quality36 저장 경로. 기존 후보와 저장은 보존합니다. 최종 품질 검수 중입니다.\n',encoding='utf-8')
subprocess.run([sys.executable,str(p),'freeze','--output',str(O/'FINAL-SOURCE-FREEZE.json')],check=True);subprocess.run([sys.executable,str(p),'build','--freeze',str(O/'FINAL-SOURCE-FREEZE.json')],check=True)
assert all(sha(R/n)==h for n,h in pins.items());assert all(sha(Path(n))==h for n,h in users.items());print('PACKAGE36 COMPLETE',flush=True)
