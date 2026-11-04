from pathlib import Path
import json, shutil, hashlib

ROOT=Path('C:/Project/d2r-combat-baseline')
BASE=ROOT/'plans/chapter1-quality04-20261101-01'
OUT=BASE/'full16'
BACK=Path('C:/Project/game-research/implementation-backups/chapter1-full16-before-20261101-01')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,value):
    assert not p.exists(),p
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

assert not OUT.exists() and not BACK.exists()
pins=json.loads((BASE/'full14/FINAL-SOURCE-FREEZE.json').read_text(encoding='utf-8'))
assert all(sha(ROOT/n)==h for n,h in pins.items())
actor=json.loads((BASE/'cold16/actors01/RESULT.json').read_text(encoding='utf-8'))
assert actor['same_full_core_start_and_end'] and all(actor['checks'].values())
for folder in ['prototype02','semantic05']:
    result=json.loads((BASE/'cold16'/folder/'result.json').read_text(encoding='utf-8'))
    assert not result['failures']
extras=['chapter1/core/chapter_run_quality16.gd','chapter1/view/chapter_elements_quality16.gd','chapter1/view/chapter_hud_quality16.gd','chapter1/view/chapter_actors_quality16.gd']
OUT.mkdir();BACK.mkdir(parents=True)
p=ROOT/'chapter1/chapter_one_view.gd'
shutil.copy2(p,BACK/'chapter_one_view.gd')
write(BACK/'manifest.json',{'before':{'chapter1/chapter_one_view.gd':sha(p)},'source14_freeze_sha256':sha(BASE/'full14/FINAL-SOURCE-FREEZE.json'),'new_files':{n:sha(ROOT/n) for n in extras}})
s=p.read_text(encoding='utf-8')
for old,new in [('core/chapter_run.gd','core/chapter_run_quality16.gd'),('view/chapter_hud.gd','view/chapter_hud_quality16.gd'),('view/chapter_elements_quality14.gd','view/chapter_elements_quality16.gd'),('view/chapter_actors_quality12.gd','view/chapter_actors_quality16.gd')]:
    assert s.count('res://chapter1/'+old)==1
    s=s.replace('res://chapter1/'+old,'res://chapter1/'+new)
p.write_text(s,encoding='utf-8')
s=(BASE/'full14/package_full14.py').read_text(encoding='utf-8')
s=s.replace('candidate14','candidate16').replace('20261101-14','20261101-16').replace('Quality14','Quality16').replace('==99','==103')
s=s.replace("'chapter1/view/arc_quality14.gdshader']","'chapter1/view/arc_quality14.gdshader',"+','.join(repr(n) for n in extras)+']')
s=s.replace('same Chapter09 gameplay and13boss, with centered faceted frost/actual frozen crystals and shatter chunks, bounded bright arc paths and smaller cold/arc contact accents.','evolved cold direct kills cause bounded actual shatter at 50% ordinary /25% elite damage; actual .48s chunks and .22s ordinary cold corpse fade, accurate HUD; inherited13boss/14FX and unchanged fire/arc rules.')
needle="    credits=OUTPUT/'credits';credits.mkdir()"
addition='''    for primary,expected in [('frost',(23862,3451,12)),('arc',(22568,3380,12))]:
        report=execute('packaged-full-'+primary,[exe,'--headless','--fixed-fps','60','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-primary=chapter1.skill.'+primary,'--chapter1-seed=90131','--chapter1-quit-after=500'],180)
        assert not report['stderr'],report['stderr']
        rows=[json.loads(line.split('FULL_CHAPTER_RUNTIME_RESULT ',1)[1]) for line in report['stdout'].splitlines() if 'FULL_CHAPTER_RUNTIME_RESULT ' in line]
        first=next(row for row in rows if row['mode']=='victory')
        assert (first['tick'],first['kills'],first['growth']['level'])==expected,first
        write(PROOF/('full-'+primary+'-proof.json'),{'first_victory':first,'scope':'Actual packaged release headless fixed60, normal policy defaultHP/earned growth; not GPU/manual/audio/performance approval.'})

'''
assert s.count(needle)==1
s=s.replace(needle,addition+needle)
(OUT/'package_full16.py').write_text(s,encoding='utf-8')
shutil.copy2(BASE/'full14/run_runtime.py',OUT/'run_runtime.py')
(OUT/'RUN.ko.md').write_text('''# 잿빛 회랑 · 제1장 후보16

실행: AshenCloister-Chapter1.exe. 기본 조작/장비/보관함은 게임 안내를 따릅니다.

진화 냉기의 직접 처치도 실제 파쇄를 만듭니다. 반경3.5m, 제한된 대상/동일 타격 예산, 파편 일반50%·정예25%이며 재귀 연쇄하지 않습니다. 기존 비진화 빙결 파쇄와 화염·번개 규칙은 유지합니다.
냉기 처치 일반 적의 사체는 약0.22초에 소멸하며 실제 파쇄의 큰 얼음 파편은0.48초 남습니다. 영웅·정예·최종 보스는 이 사체 처리에서 제외합니다.

후보14/이전 실행·증거·저장을 보존했습니다. 후보16은 별도 저장 namespace를 사용합니다. 기존 저장을 자동 복사하지 않습니다.
이는 품질 검수 중인 실행 후보이며 SACRATA 품질, 수동 전체 플레이, 실청취, 정식 성능 승인을 뜻하지 않습니다.
''',encoding='utf-8')
write(OUT/'ADOPTION.json',{'backup':str(BACK),'source14_preserved_except_intentionally_adopted_view':all(sha(ROOT/n)==h for n,h in pins.items() if n!='chapter1/chapter_one_view.gd'),'new_files':extras,'actor_evidence':str(BASE/'cold16/actors01/RESULT.json'),'scope':'16 assembly adopted; package and full validation pending.'})
print(str(OUT),flush=True)
