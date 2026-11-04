from pathlib import Path
import json,shutil,hashlib
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OLD=BASE/'full11';OUT=BASE/'full12'
BACK=Path('C:/Project/game-research/implementation-backups/chapter1-full12-before-20261101-01')
assert not OUT.exists()and not BACK.exists();OUT.mkdir();BACK.mkdir(parents=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
freeze=json.loads((OLD/'FINAL-SOURCE-FREEZE.json').read_text(encoding='utf-8'))
assert all(sha(ROOT/n)==h for n,h in freeze.items())
p=ROOT/'chapter1/chapter_one_view.gd';shutil.copy2(p,BACK/'chapter_one_view.gd')
with(BACK/'manifest.json').open('x',encoding='utf-8')as f:json.dump({'source11_freeze':str(OLD/'FINAL-SOURCE-FREEZE.json'),'source11_freeze_sha256':sha(OLD/'FINAL-SOURCE-FREEZE.json'),'before':{'chapter1/chapter_one_view.gd':sha(p)}},f,indent=2)
text=p.read_text(encoding='utf-8');assert text.count('res://chapter1/view/rigged_hero_actors.gd')==1
p.write_text(text.replace('res://chapter1/view/rigged_hero_actors.gd','res://chapter1/view/chapter_actors_quality12.gd'),encoding='utf-8')
ignore=ROOT/'chapter1/art/chained_warden/v01/.gdignore'
if ignore.exists():shutil.move(str(ignore),str(BACK/'chained-warden-research.gdignore'))
s=(OLD/'package_full11.py').read_text(encoding='utf-8').replace('candidate11','candidate12').replace('20261101-11','20261101-12').replace('Quality11','Quality12').replace('==92','==95')
extra=['chapter1/view/chapter_actors_quality12.gd','chapter1/art/chained_warden/v01/chained_demon_animated.glb','chapter1/art/chained_warden/v01/ATTRIBUTION.ko.md']
s=s.replace("'chapter1/view/contact_quality10.gdshader']","'chapter1/view/contact_quality10.gdshader',"+','.join(repr(x)for x in extra)+']')
s=s.replace('chapter1/art/rigged_mage/v01/*.md\"','chapter1/art/rigged_mage/v01/*.md,chapter1/art/chained_warden/v01/*.md\"')
s=s.replace("shutil.copy2(HERE/'RUN.ko.md',OUTPUT/'RUN.ko.md')","shutil.copy2(ROOT/'chapter1/art/chained_warden/v01/ATTRIBUTION.ko.md',credits/'ATTRIBUTION-Chained-Warden.ko.md')\n    shutil.copy2(HERE/'RUN.ko.md',OUTPUT/'RUN.ko.md')")
anchor="    credits=OUTPUT/'credits';credits.mkdir()"
addition='''    full=execute('packaged-full-normal',[exe,'--headless','--fixed-fps','60','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-seed=90131','--chapter1-quit-after=500'],180)
    states=[json.loads(line.split('FULL_CHAPTER_RUNTIME_RESULT ',1)[1]) for line in full['stdout'].splitlines() if 'FULL_CHAPTER_RUNTIME_RESULT ' in line]
    victory=next(row for row in states if row['mode']=='victory')
    assert victory['tick']==21749 and victory['kills']==3185 and victory['growth']['level']==11
    rigs=[json.loads(line.split('CHAPTER1_WARDEN_RIG ',1)[1]) for line in full['stdout'].splitlines() if 'CHAPTER1_WARDEN_RIG ' in line]
    assert len(rigs)==1 and rigs[0]['bones']==73 and len(rigs[0]['clips'])==8
    write(PROOF/'full-release-proof.json',{'result':victory,'warden':rigs,'scope':'Packaged release headless fixed60 normal policy; final boss really created/loaded, not manual/GPU/performance/audio approval'})
'''
assert s.count(anchor)==1;s=s.replace(anchor,addition+'\n'+anchor)
s=s.replace('same Chapter09 gameplay; rigged hero, procedural staff/tapered grass, contact flashes, shaded paving and MSAA4x.','same Chapter09 gameplay plus unique final-boss73bone/eightclip presentation, paid release timing and freeze/thaw continuity; hero/grass/contact presentation retained from11.')
(OUT/'package_full12.py').write_text(s,encoding='utf-8')
(OUT/'run_runtime.py').write_text((OLD/'run_runtime.py').read_text(encoding='utf-8'),encoding='utf-8')
(OUT/'RUN.ko.md').write_text('''# 잿빛 회랑 · 전체1장 후보12

AshenCloister-Chapter1.exe 실행 후 화염/냉기/번개를 선택합니다.
WASD/방향키·좌클릭 이동, Space 회피, Q 회복약, E 가까운 선택 의식,
I 장비, Esc 정지, M 음소거. 세 봉인·정예2·최종 보스를 실제 처치하면 완료입니다.

후보11의 영웅/식생/타격을 유지하고 최종 보스만73골격의 사슬·가면형으로 바꿨습니다.
대기/보행/두 전조/내려치기/부채 공격/피격 반응/사망과 빙결·해빙의 동작 연결을 검수 중입니다.
정예2와 일반 적은 기존 스프라이트입니다. SACRATA 최종 품질 승인이 아닙니다.
후보12는 새 전용 저장을 사용합니다. 기존 Baseline/후보11 저장은 읽거나 변환하지 않습니다.
이전 실행본·증거는 그대로 보존했습니다. 수동 전체 플레이·실청취·정식 성능은 별도 검수 항목입니다.
원 모델 Mophs/Chained Demon의 선택 라이선스CC BY3.0은 credits/ATTRIBUTION-Chained-Warden.ko.md,
영웅의 CC BY-SA3.0은 credits/ATTRIBUTION-Rigged-Mage.ko.md를 따릅니다.
''',encoding='utf-8')
print(str(OUT))
