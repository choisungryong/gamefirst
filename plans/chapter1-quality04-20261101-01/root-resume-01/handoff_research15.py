from pathlib import Path
import json,hashlib,shutil
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'elements15'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
assert read(OUT/'normal01/gpu-execution.json')=={'actual_exit':0,'stderr_bytes':0}
assert not read(OUT/'caps01/result.json')['failures']
comparison=read(OUT/'compare14-partial01/RESULT.json');assert all(comparison['same'].values())
pins=read(BASE/'full14/FINAL-SOURCE-FREEZE.json');assert all(sha(ROOT/n)==h for n,h in pins.items())
source=read(OUT/'normal01/source.json');stage=Path(source['stage']);assert all(sha(stage/n)==h for n,h in source['pins'].items())
status='''# 15 연구 · 실제 냉기 처치 잔해 연결, 패키지/시각 승인은 아직

현재 기본 실행은 후보14이며 rootchapter_one_view의Effects preload도14다.15는별도연구소스 chapter1/view/chapter_elements_quality15.gd다.14의99개런타임과rootmain/preset freeze는그대로다. 기존14/13/원본/실패/사용자저장을보존했다. 목표active/품질미달이다.

14정상냉기에서실제shatter0/일반적살아있는빙결0틱을발견해작업순서를실전냉기피드백으로정정했다. 15는진화냉기실제death와바로앞paid hit의seq/target/skill/evolved스냅샷이맞을때만큰얼음조각/작은지면흔적을연결한다. 추가피해/빙결0이며실제shatter와중복하지않는다. 이것은처치잔해이며기존빙결/파쇄damageproc라고부르지않는다. 소비4/기존128조각상한을공유한다.

`normal01/` 실제sourceGPU 기본HP/정상선택·장착pilot/seed90131/냉기주력/저장off/190초 부분진행은tick11400/1376kill,종료0/stderr0/18PNG다. 지급HP/rank없다. 새처치잔해690회,실제shatter0유지,정예빙결101틱/일반빙결0틱.14동일조건190초패키지headless참조와10전투상태가모두같다(`compare14-partial01/RESULT.json`). 190초를전체1장/15패키지/수동/성능승인으로세지않는다.

`caps01/`12개검사/실패0/종료0/stderr0. paid snapshot·대상/seq/skill불일치거절·비진화거절·실제shatter와중복안함·replay중복안함·상한·reset·core불변을확인했다. synthetic이므로실전품질증거와구분한다.14의검사오디오경고를되풀이하지않도록제품audio.reset/실제200msrelease를쓴다.

시각검수한계: 고정시각150초의14/15화면과15state0011/90초는공격사이순간이라새짧은죽음연출을충분히보여주지않았다. 690카운터를미술품질승인으로바꾸지않는다. **다음은실제cold_death_accents증가직후한프레임에맞춘배치/영상을정상기본HP·실제획득성장으로수집하는것**이다. 연구HP140/지급랭크로성공장면을만들지않는다. 원한다면정상pilot를core로120초재시뮬레이션한뒤동일상태에서14대15의짧은오프라인전후영상을만들수있으나,그조건을표시하고전체실시간/성능/수동으로부르지않는다. 실제계속된정상GPU를이벤트에맞춰캡처하는방법도가능하다.

그뒤필요시파편크기/색/지면잔광을수정하고,새15freeze/EXE/전체냉기정상·회귀/도감v08·인계를만든다. 아직15EXE없음. 이후일반/정예동작·공간깊이·파밍/보상UX·수동전체/실청취/최종1080p3회·네이티브stash/CAS검수를진행한다.

14정식증거는full14/STATUS.ko.md,실제GPU6분52초/3632kill/24PNG/0,full14/COLD-FIELD-FINDING.ko.md의0파쇄한계,도감v07(10페이지/176local refs missing0),profile-process02(31검사/3processbackend재시작·3장비유지/다음전투적용)다. profile실제MSIX경로정정은PATH-CORRECTION.json. 네이티브stashUI/CAS/전원손실은열림. 기존원작영상관찰/모델라이선스는full13/11장부를계승한다.

현재15 import/check/GPU/headless참조/caps는모두terminal이다. 동일경로재실행/이전stage수정금지. 임시book탭3닫힘/viewportreset/8784서버중지. 기존탭1(oldlocalhost8768)미변경. agents미사용/root단독/루트전체editorimport금지/보호자산복사·커밋·업로드·구매없음. 이번목표턴은14제품/영상/도감/저장·실전한계발견·15실제소스/검증의progress다.
'''
p=OUT/'STATUS.ko.md';assert not p.exists();p.write_text(status,encoding='utf-8')
BACK=Path('C:/Project/game-research/implementation-backups/chapter1-research15-docs-before-20261101-01');assert not BACK.exists();BACK.mkdir(parents=True)
prefix='''# 2026-11-01 최신 —15 실전 냉기 처치 연구 종료/부분통과 · 기본EXE14 유지 · 목표 active

먼저 `plans/chapter1-quality04-20261101-01/elements15/STATUS.ko.md`를 읽는다.15sourceGPU190초는11400틱/1376kill/처치잔해690회/18PNG/종료0/stderr0,14동일조건패키지참조와10전투상태동일. 별도12개paid hit/death/dedupe/상한/reset/core불변검사도0/stderr0다. 정상기본HP/실제획득성장이며지급빌드아님. 그러나15EXE/전체1장/미술·수동·실청취·성능승인은아니다.

15의새파일 chapter1/view/chapter_elements_quality15.gd는진화냉기실제처치에만얼음잔해를연결한다. 기존실제빙결/shatter피해규칙은바꾸지않아실제shatter0유지다.14에서실전0파쇄가발견된까닭에다음우선순위를정정했다.690카운터만으로화려함을승인하지않는다. 고정150초/90초/state0011화면은짧은연출사이순간이라충분한증거가아니다. 다음은**실제처치event직후캡처/짧은14대15정상전투영상**으로시각판정→필요시보완→15별도freeze/EXE/전체검증/도감갱신이다.14기존EXE·freeze·rootpreload는그대로다.

elements15/normal01(source/GPU),compare14-partial01(10상태비교),caps01(12검사)는모두terminal이며새경로없이재실행하지않는다. root14freeze/source15stage소스핀모두일치. 이전14본문/증거를아래exact bytes suffix로유지했다. 상세14실제GPU6분52초/3632kill·0파쇄한계·저장backend3process31검사/도감v07과열린품질관문은아래및full14문서를따른다. 목표active,2·3장미착수.

---

'''
history={}
for n in ['HANDOFF.md','chapter1/FULL-CHAPTER.ko.md']:
 p=ROOT/n;old=p.read_bytes();dest=BACK/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(old);p.write_bytes(prefix.encode('utf-8')+old);assert p.read_bytes().endswith(old);history[n]={'old_sha256':sha(dest),'new_sha256':sha(p),'exact_old_suffix':True}
p=OUT/'HANDOFF-PRESERVATION.json';assert not p.exists();p.write_text(json.dumps({'backup':str(BACK),'files':history,'root14_freeze_matches':True,'stage15_source_pins_match':True},indent=2),encoding='utf-8')
p=OUT/'DELIVERABLES.json';assert not p.exists();p.write_text(json.dumps({'status':str(OUT/'STATUS.ko.md'),'goal':'active','current_exe':str(ROOT/'builds/chapter1/chapter1-full-candidate-20261101-14/AshenCloister-Chapter1.exe'),'new_source':'chapter1/view/chapter_elements_quality15.gd','source_sha256':sha(ROOT/'chapter1/view/chapter_elements_quality15.gd'),'partial_seconds':190,'kills':1376,'cosmetic_cold_death_accents':690,'real_shatter':0,'actual_gpu_exit0_stderr0':True,'source_pins_match':True,'comparison10_all_same':True,'caps_checks':12,'next':'Actual cold-death event-synchronous image/video using normal defaultHP/earned build; then15package/full verification/book. Do not claim counter or190secondspartial as final quality/full chapter.'},indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'source15_pins_match':True,'source14_freeze_matches':True,'partial_seconds':190,'cosmetic_accents':690,'real_shatter':0,'goal':'active'}),flush=True)
