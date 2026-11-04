from pathlib import Path
import json,shutil,hashlib
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OLD=BASE/'full12';OUT=BASE/'full13'
BACK=Path('C:/Project/game-research/implementation-backups/chapter1-full13-before-20261101-01')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not OUT.exists()and not BACK.exists()
pins=json.loads((OLD/'FINAL-SOURCE-FREEZE.json').read_text(encoding='utf-8'))
changed=[n for n,h in pins.items()if sha(ROOT/n)!=h]
assert changed==['chapter1/view/chapter_actors_quality12.gd'],changed
for path in ['visibility06','clock07','gpu09']:
 r=json.loads((BASE/'boss-research12'/path/'result.json').read_text(encoding='utf-8'));assert not r['failed']
OUT.mkdir();BACK.mkdir(parents=True)
shutil.copy2(ROOT/changed[0],BACK/'chapter_actors_quality12.gd')
(BACK/'manifest.json').write_text(json.dumps({'before13':{n:sha(ROOT/n)for n in pins},'changed_since12':changed,'candidate12_preserved_stage_actor':str(Path('C:/Project/game-research/build-staging/chapter1-full-candidate-20261101-12')/changed[0]),'candidate12_expected_actor_sha256':pins[changed[0]]},indent=2),encoding='utf-8')
s=(OLD/'package_full12.py').read_text(encoding='utf-8').replace('candidate12','candidate13').replace('20261101-12','20261101-13').replace('Quality12','Quality13')
s=s.replace("    write(PROOF/'full-release-proof.json',{'result':victory,'warden':rigs,", "    deaths=[json.loads(line.split('CHAPTER1_WARDEN_DEATH_POSE ',1)[1])for line in full['stdout'].splitlines()if 'CHAPTER1_WARDEN_DEATH_POSE 'in line]\n    assert len(deaths)==1 and deaths[0]['mode']=='victory' and deaths[0]['visual_age']>=deaths[0]['clip_length']\n    write(PROOF/'full-release-proof.json',{'result':victory,'warden':rigs,'terminal_death':deaths,")
s=s.replace('paid release timing and freeze/thaw continuity;','paid release timing, freeze/thaw continuity, posed-capsule owner coverage and terminal-clock-independent death;')
(OUT/'package_full13.py').write_text(s,encoding='utf-8')
shutil.copy2(OLD/'run_runtime.py',OUT/'run_runtime.py')
s=(OLD/'RUN.ko.md').read_text(encoding='utf-8').replace('후보12','후보13')
s+='\n13은 과도한 보스 투명화를 현재 자세의 실제 겹침 판정으로 고쳤습니다. 승리로 전투 시간이 멈춰도 보스 사망 동작이 끝까지 진행됩니다.\n'
(OUT/'RUN.ko.md').write_text(s,encoding='utf-8')
print(str(OUT))
