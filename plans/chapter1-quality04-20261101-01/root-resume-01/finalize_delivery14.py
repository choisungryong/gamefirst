from pathlib import Path
import json,hashlib,shutil,importlib.util,re
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'full14';BOOK=OUT/'book-v07/dist';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
spec=importlib.util.spec_from_file_location('package14',OUT/'package_full14.py');package=importlib.util.module_from_spec(spec);spec.loader.exec_module(package)
package.check(ROOT,read(OUT/'FINAL-SOURCE-FREEZE.json'));selected=package.preservation()
stages={};exes={}
for n in [11,12,13,14]:
 pins=read(BASE/f'full{n}/build/staging-manifest.json');stage=Path(f'C:/Project/game-research/build-staging/chapter1-full-candidate-20261101-{n:02d}');package.check(stage,pins);stages[str(n)]={'count':len(pins),'mismatches':[]}
for n in [9,11,12,13,14]:
 b=read(BASE/f'full{n:02d}/build/build.json');assert sha(b['exe'])==b['sha256'];exes[str(n)]={'sha256':b['sha256'],'bytes':b['bytes']}
write(OUT/'FINAL-PRESERVATION.json',{'source14_freeze_matches':True,'source15_outside14_frozen_runtime':True,'selected_historical_pins':selected,'stages':stages,'exes':exes,'scope':'Selected backups/baseline/exes/old profiles and stage source manifests; not every historical generated Godot log/sidecar. QA profile namespaceB and raw failures retained; no user save migration.'})
refs=[];missing=[]
for p in BOOK.glob('*.html'):
 for ref in re.findall(r'(?:src|href)="([^"]+)"',p.read_text(encoding='utf-8')):
  if ref.startswith(('http:','https:','#','data:')):continue
  refs.append((p.name,ref))
  if not(p.parent/ref.split('#')[0]).resolve().is_file():missing.append((p.name,ref))
assert not missing,missing
qa=read(OUT/'book-v07/BROWSER-QA.json');assert len(qa['pages'])==20 and all(r['scrollWidth']<=r['width']for r in qa['pages'])and qa['video']['ended']
write(OUT/'book-v07/REVISION-03.json',{'pages':10,'local_references':len(refs),'missing':missing,'browser_initial':'BROWSER-QA.json','final_browser_patch_review':{'elements_reloaded_gap_note_visible':True,'index_actual_gpu_image':True,'index_1440_scrollWidth':1425,'index_390_scrollWidth':375,'owned_tab3_closed':True,'viewport_reset':True},'initial_status_and_HTML_preserved':['BUILD.json','revision-02-before','revision-03-before','../STATUS-initial-GPU-pending.ko.md','../STATUS-before-field-finding.ko.md'],'files':{str(p.relative_to(BOOK)).replace('\\','/'):sha(p)for p in BOOK.rglob('*')if p.is_file()},'scope':'14actualcold result and honest0shatter field gap added. 13s video reached browser end;20navigation/width cases plus finalpatch index widths. No all-offscreen/audio/print/manual/performance approval.'})
BACK=Path('C:/Project/game-research/implementation-backups/chapter1-full14-docs-before-20261101-01');assert not BACK.exists();BACK.mkdir(parents=True)
prefix='''# 2026-11-01 최신 — 후보14 원소 개선/실전 한계 발견 ·15 정상연구 진행 · 목표 active

먼저 `plans/chapter1-quality04-20261101-01/full14/STATUS.ko.md`와`COLD-FIELD-FINDING.ko.md`를읽는다. 최신EXE는 `builds/chapter1/chapter1-full-candidate-20261101-14/AshenCloister-Chapter1.exe`, SHA `5fa58077545ea3cc3c0d55bc6abbd5bc57eab32bdd78c8ccdbfa398ca28f5952`,129994088bytes/runtime99/stage101/PCK176.13/시각보류12/과거실행·원본·실패·사용자저장보존. 목표active/품질미달,2·3장미착수. 직전과현재턴은실제제품/증거가바뀐progress다.

14는새FX4파일 chapter_elements_quality14.gd/comet_quality14/impact_quality14/arc_quality14다. 냉기창면/중심·실제빙결24×4얼음/48records·실제파쇄128조각·paidarc.targets64links/.20초·냉기번개contactconsume3/.68,.55크기로연결. fire/적탄분기·core/data/profile·13보스/영웅/환경그대로. 루트chapter_one_view의Effects preload만14로변경,rootmain/preset은Baseline.14freeze모두일치,15새소스는closure밖이다.

14실제GPU냉기정상seed90131은24749틱/412.4833초(6분52초)/3632처치/Lv12/24PNG/종료0/stderr0. 같은시드13EXE headless참조와10전투상태동일. 옛09냉기는seed71/427초라개선율/동일시드비교금지. release기본화염500simsec도21749틱/3185/Lv11/stderr0.13골격보스/terminal사망유지. 자동정책/저장off이며수동전체/실청취/성능승인아님.

**핵심발견:**14같은정상입력의읽기전용observer가GPU10상태를그대로유지하며 실제shatter0/일반적살아있는빙결0틱/정예545틱/동시빙결최대1/얼음최대4로집계했다. 진화28피해가일반12/18HP를1회,돌격32HP도누적빙결전처치해연구HP140의파쇄19회가실전에이어지지않는다. 연구화려함을정상품질로확대하지않는다. `full14/cold-observer01`과`COLD-FIELD-FINDING.ko.md`가권위근거다. 다음우선순위는일반모델보다**실제냉기처치/성장피드백**으로정정한다.

15연구source `chapter1/view/chapter_elements_quality15.gd`는바로앞실제hit의seq/target/evolved스냅샷과일치하는진화냉기death에얼음잔해/작은지면흔적을연결한다. 추가피해/빙결0,실제shatter와중복안함,consume최대4/기존128조각공유. 처치잔해를빙결/파쇄damageproc라고부르지않는다. rootpreload는14고정. `elements15/normal01/` source.json과GPU launch/execution을먼저재검증한다. 외부stage `C:/Project/game-research/build-staging/chapter1-elements15-normal-20261101-01`,스크립트run_elements15_normal01.py,import/check통과,실제GPU190wallsec부분정상실행을시작했다(기본HP/실제획득성장/seed90131/저장off,지급빌드아님). 실행이끝났다고추측하거나동일출력을재시작하지말고현재PID/결과로판정한다.15EXE/전체1장승인아직없음.

14연구arena02/04는80배치적140HP/.75speed·영웅5000HP·지급진화냉기4/8초후번개4·성장선택억제13초다. 실제core결정빙결hit184/shatter19/동시11/48kill,전후7상태동일. GPU04 15PNG/0/stderr0. 전후movie05 13초오프라인30FPS/390frames/1280×428/오른쪽audio만. 동일core이며원본AVI/로그/encoder실패판정부존. ffmpeg정보stderr를helper가오류취급했지만actual0/완성MP4를ffprobe검증해재인코딩없이확정했다. 이연구는정상한판/획득성장/실제성능아님.

14release-caps02는13검사/0/actual0/stderr0(상한/중복/정지/해빙/초기화/코어불변). arena03/release-caps01의ObjectDB는verbose로AudioStreamWAV/PlaybackWAV확인. 검사가제품audio.reset의정지voiceunpause/실제시계release대기를우회했다. 동일절차적용후02quiet,제품14freeze/EXE수정안함. 모든상황누수0주장아님. 첫arena01step인자/짙은얼음/겹친별등실패원본보존.

추가저장backend: `full14/profile-process02/RESULT.json`,독립3Godot프로세스/31검사/모두0/stderr0. 실제defaultuser경로고유3장비선택→새프로세스ChapterRun적용(화염2발)→receipt재생no-op/패배후starter중복없음→세번째재시작3개유지. **네이티브stashUI/동시CAS/전원손실은여전히미검수.** 실제QA경로는MSIX리디렉션 `C:/Users/twins/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Roaming/AshenCloisterChapterOneProfileProcessQA20261101B`;실제OS반환경로와고유basename검증뒤snapshot. source.json의초기Python Godot/app_userdata가정/RESULT의directRoaming설명은PATH-CORRECTION.json으로정정. 첫프로브예약어namespace실패/A로그와잘못가정한수집경로오류도보존. 사용자본래저장미접근/변환없음.

도감v07 `plans/chapter1-quality04-20261101-01/full14/book-v07/dist/index.html`10페이지(냉기·번개추가),초기BUILD/상태pending/HTMLrevision02/03전보존. 정상냉기0파쇄한계를표지·원소·검증에명시. 전후13초영상이브라우저끝13초에도달.1440desktop/390mobile10제목·탐색/폭20case,최종표지2폭추가확인. 기존13/11화면·24초09대연구05영상은원번호유지. 최종로컬참조누락0/REVISION03. 소유탭3닫고viewportreset,8784서버검수후정리. 기존탭1(oldlocalhost8768)미변경. 모든offscreen미디어/실청취/인쇄/성능승인아님.

15실전냉기개선후일반/정예동작·공간깊이·장비스크롤/고유발견·보스사망→보상리듬,수동5–8분/실청취/최종1080p3회성능·네이티브stash재시작/CAS를진행한다. 기술검사/연구부하로목표품질대신승인하지않는다. agents미사용/root단독. 루트전체editorimport/기존출력재실행/보호자산복사/커밋/업로드/구매금지.

아래 이전 본문은 exact bytes suffix로 보존했다.

---

'''
history={}
for name in ['HANDOFF.md','chapter1/FULL-CHAPTER.ko.md']:
 p=ROOT/name;old=p.read_bytes();target=BACK/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(old);p.write_bytes(prefix.encode('utf-8')+old);assert p.read_bytes().endswith(old);history[name]={'old_sha256':sha(target),'new_sha256':sha(p),'exact_old_suffix':True}
write(OUT/'HANDOFF-PRESERVATION.json',{'backup':str(BACK),'files':history})
write(OUT/'DELIVERABLES.json',{'build':read(OUT/'build/build.json'),'status':str(OUT/'STATUS.ko.md'),'book':str(BOOK/'index.html'),'gpu_cold_seconds':read(OUT/'GPU-COLD-RESULT.json')['result']['tick']/60,'field_gap_actual_shatter':0,'next_source15':'chapter1/view/chapter_elements_quality15.gd','goal':'active','artifact_hashes':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p)for p in [OUT/'STATUS.ko.md',OUT/'SACRATA-COMPARISON.ko.md',OUT/'COLD-FIELD-FINDING.ko.md',OUT/'GPU-COLD-RESULT.json',OUT/'FINAL-PRESERVATION.json',OUT/'HANDOFF-PRESERVATION.json',OUT/'profile-process02/RESULT.json',OUT/'profile-process02/PATH-CORRECTION.json',OUT/'book-v07/REVISION-03.json',ROOT/'chapter1/art/QUALITY14-LEDGER.json']}})
print(json.dumps({'book_local_refs':len(refs),'missing':missing,'source14_matches':True,'handoff_preserved':True,'goal':'active'}),flush=True)
