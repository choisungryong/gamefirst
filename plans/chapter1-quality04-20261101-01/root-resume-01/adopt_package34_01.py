from pathlib import Path
import json,hashlib,shutil,re,subprocess,sys
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';O=B/'full34';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(R/n)==h for n,h in read(B/'full33/FINAL-SOURCE-FREEZE.json').items())
assert read(B/'monster34/directions02/proof/RESULT.json')['passed'] and read(B/'monster34/mapped03/COMPARISON.json')['passed']
assert all(r['core_equal'] for r in read(B/'monster34/cost01/COMPARISON.json')['runs'])
actor='chapter1/view/chapter_actors_quality34b.gd';assert sha(R/actor)==read(B/'monster34/cost01/source.json')['pins'][actor]
backup=Path('C:/Project/game-research/implementation-backups/chapter1-before34-20261105-01');assert not backup.exists() and not O.exists();backup.mkdir();O.mkdir()
pins=read(B/'full33/ADOPTION.json')['preserved_exes'];build=read(B/'full33/build/build.json');pins[str(Path(build['exe']).relative_to(R)).replace(chr(92),'/')]=build['sha256'];assert all(sha(R/n)==h for n,h in pins.items())
for n in ['chapter1/chapter_one_view.gd','project.godot','export_presets.cfg']:
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,p)
shutil.copy2(B/'full33/FINAL-SOURCE-FREEZE.json',backup/'root33-freeze.json')
users={}
for ns in ['AshenCloisterChapterOneQuality23','AshenCloisterChapterOneQuality29']:
 folder=Path('C:/Users/twins/AppData/Roaming')/ns;assert folder.exists();dest=backup/'user-profiles'/ns;dest.mkdir(parents=True)
 for p in folder.glob('chapter-one-profile-v1*.json'):shutil.copy2(p,dest/p.name);users[str(p)]=sha(p)
assert len(users)>=6
p=R/'chapter1/chapter_one_view.gd';s=p.read_text(encoding='utf-8');assert s.count('chapter_actors_quality32b.gd')==1;p.write_text(s.replace('chapter_actors_quality32b.gd','chapter_actors_quality34b.gd'),encoding='utf-8')
(O/'ADOPTION.json').write_text(json.dumps(dict(backup=str(backup),preserved_exes=pins,user_pins=users,tested_actor_sha256=sha(R/actor),scope='Actor32b to34b only: skeletal axe walker family on existing144 walker roots; ranged/charger/elite/boss retained. CC0 KevDev model/9authoredclips, canonical1mesh2surfaces. Original core16/World31d/HUD27/Input21/FX33b, paid timing, hit/freeze/cold corpse/pool224 retained. Final quality gates open.'),indent=2),encoding='utf-8')
s=(B/'full33/package_full33.py').read_text(encoding='utf-8').replace('chapter1-full-candidate-20261105-33','chapter1-full-candidate-20261105-34').replace('Quality33','Quality34').replace('candidate33 workflow','candidate34 workflow').replace('==135','==141')
s=s.replace("'chapter1/view/chapter_elements_quality33b.gd']","'chapter1/view/chapter_elements_quality33b.gd','chapter1/view/chapter_actors_quality34b.gd','chapter1/art/skeleton_outlaw/v02/skeleton_outlaw_merged.glb','chapter1/art/skeleton_outlaw/v02/ATTRIBUTION.ko.md','chapter1/art/skeleton_outlaw/v02/DERIVATION.json','chapter1/art/skeleton_outlaw/v01/ATTRIBUTION.ko.md','chapter1/art/skeleton_outlaw/v01/SOURCE.json']")
s=s.replace('chapter1/art/chained_warden/v01/*.md','chapter1/art/chained_warden/v01/*.md,chapter1/art/skeleton_outlaw/v01/*.md,chapter1/art/skeleton_outlaw/v01/*.json,chapter1/art/skeleton_outlaw/v02/*.md,chapter1/art/skeleton_outlaw/v02/*.json')
s=re.sub(r'^SCOPE=.*$',"SCOPE="+repr('Candidate34: Core16/World31d/Actor34b/HUD27/Input21/FX33b. Distinct CC0 skeletal axe walker body and authored gait/swing/hit/death. Other roles/boss remain32b. Paid core timing, pool224, cold fade and all combat/generation/save rules retained. Source direction/pose/core tests passed; actual whole/manual/hearing/final focused performance remain separate.'),s,flags=re.M).replace('Only fire/ground loot presentation changed from32. Prior core16 results retain their scope; no new full33 whole run claimed.','Only walker family presentation changed from33. Prior core16 results retain their scope; no new full34 whole run claimed.')
s=s.replace("shutil.copy2(HERE/'RUN.ko.md',OUTPUT/'RUN.ko.md')", "(credits/'ATTRIBUTION-Skeleton-Outlaw.ko.md').write_text('# Skeleton Outlaw\\n\\nKevDev (Kevin Iglesias), CC0. https://opengameart.org/node/89457\\nBody/axe images and9 author clips preserved. Native ufbx conversion, hair/MetalJaw removed, canonical bind-space mesh consolidation to1mesh2surfaces. Head.72 is runtime only. Other provenance files: SOURCE-Skeleton-Outlaw.json and DERIVATION-Skeleton-Outlaw.json.\\n',encoding='utf-8')\n    shutil.copy2(ROOT/'chapter1/art/skeleton_outlaw/v01/SOURCE.json',credits/'SOURCE-Skeleton-Outlaw.json')\n    shutil.copy2(ROOT/'chapter1/art/skeleton_outlaw/v02/DERIVATION.json',credits/'DERIVATION-Skeleton-Outlaw.json')\n    shutil.copy2(HERE/'RUN.ko.md',OUTPUT/'RUN.ko.md')")
p=O/'package_full34.py';p.write_text(s,encoding='utf-8');(O/'RUN.ko.md').write_text('# 후보34\n\n일반 근접 적에 해골·도끼 모델과 저작된 보행·공격·사망 동작을 반영한 검수 후보입니다. 별도Quality34 저장 경로. 이전 후보와 사용자 저장은 보존합니다. 최종 품질 검수 중입니다.\n',encoding='utf-8')
subprocess.run([sys.executable,str(p),'freeze','--output',str(O/'FINAL-SOURCE-FREEZE.json')],check=True);subprocess.run([sys.executable,str(p),'build','--freeze',str(O/'FINAL-SOURCE-FREEZE.json')],check=True)
assert all(sha(R/n)==h for n,h in pins.items());assert all(sha(Path(n))==h for n,h in users.items());print('PACKAGE34 COMPLETE',flush=True)
