from pathlib import Path
import hashlib,json,shutil,re,importlib.util
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';OUT=BASE/'full13';BOOK=OUT/'book-v06/dist'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
spec=importlib.util.spec_from_file_location('package13',OUT/'package_full13.py');package=importlib.util.module_from_spec(spec);spec.loader.exec_module(package)
pins=read(OUT/'FINAL-SOURCE-FREEZE.json');package.check(ROOT,pins)
selected=package.preservation()
stages={}
for n in [11,12,13]:
 freeze=read(BASE/f'full{n}/build/staging-manifest.json');stage=Path(f'C:/Project/game-research/build-staging/chapter1-full-candidate-20261101-{n:02d}')
 package.check(stage,freeze);stages[str(n)]={'count':len(freeze),'mismatches':[]}
exes={}
for n in [9,11,12,13]:
 build=read(BASE/f'full{n:02d}/build/build.json');p=Path(build['exe']);assert sha(p)==build['sha256'];exes[str(n)]={'sha256':sha(p),'bytes':p.stat().st_size}
write(OUT/'FINAL-PRESERVATION.json',{'source13_freeze_matches':True,'selected_historical_pins':selected,'stages':stages,'exes':exes,'scope':'Selected backups/baseline/exes/profiles and full11/12/13 stage source pins, not every historical raw sidecar or generated Godot log. No existing save migration.'})
refs=[];missing=[]
for p in BOOK.glob('*.html'):
 for ref in re.findall(r'(?:href|src)="([^"]+)"',p.read_text(encoding='utf-8')):
  if ref.startswith(('http:','https:','#','data:')):continue
  refs.append((p.name,ref))
  if not(p.parent/ref.split('#')[0]).resolve().is_file():missing.append((p.name,ref))
assert not missing,missing
qa=read(OUT/'book-v06/BROWSER-QA.json');assert len(qa['pages'])==18 and all(r['scrollWidth']<=r['width']for r in qa['pages'])
write(OUT/'book-v06/REVISION-02.json',{'local_reference_count':len(refs),'missing':missing,'pages':9,'browser_qa':'BROWSER-QA.json','files':{str(p.relative_to(BOOK)).replace('\\','/'):sha(p)for p in BOOK.rglob('*')if p.is_file()},'scope':'Final13 book after GPU result. Original BUILD and revision02-before HTML preserved. Old11 imagery/video keep labels; GPU09 images explicitly placement, actual13 header330s. Navigation/width for18cases, partial image review, not all offscreen assets/movie/audio/print approval.'})
BACK=Path('C:/Project/game-research/implementation-backups/chapter1-full13-docs-before-20261101-01');assert not BACK.exists();BACK.mkdir(parents=True)
prefix='''# 2026-11-01 최신 — 전체1장 후보13 고유 보스 · 목표 active

먼저 `plans/chapter1-quality04-20261101-01/full13/STATUS.ko.md`를 읽는다. 최신 실행은 `builds/chapter1/chapter1-full-candidate-20261101-13/AshenCloister-Chapter1.exe`, SHA `52e27a091b15642099300050e20ead742818780c21225dfd779573df2a163af1`,129980024bytes/runtime95/stage97/PCK171.11/시각보류12/과거 실행·실패·사용자 저장을 보존했다. 기능 검사만으로 SACRATA 품질을 승인하지 않는다.

최종 보스만 Mophs/Chained Demon(CC BY3.0 선택)의73골격/자체8클립 사슬·가면형으로 연결했다. 피부/가면/사슬3재질·1.15scale, 실제전조/공격event release.157초·빙결회복end연장보상·현재자세8capsule 영웅가림(근접56%,5m/옆100%)·승리후stoppedcore에서도사망재생을 반영했다. 보스 소스는 `chapter1/view/chapter_actors_quality12.gd`(이름은12,현재13freeze)이며 rootchapter_one_view preload도그파일이다. 일반/정예는11스프라이트, core/data/profile/영웅/환경/FX수치는변경없다. rootmain/preset은Baseline그대로다.

`full13/GPU-FULL-RESULT.json`: 실제 패키지GPU 정상화염21749틱/362.4833초/3185처치/Lv11,첫승리10상태항목11과동일,종료0/stderr0/22PNG. 보스73골격8클립과victory사망1.125초완료로그1.1362초확인. root가330초12/13화면을비교해과도한유령fade해소확인. 즉시승리모달은죽음/보상리듬을덮으므로추가개선대상. 자동정책/저장off이며수동전체·실청취·성능승인아님. release30초/외부7동작/전체500simsec도통과.

`boss-research12/visibility06`배치/terminal11검사,`clock07`실제ChapterRun.step 빙결해빙8검사,`gpu09`8PNG/actual0/stderr0. gpu08은카메라delta0이라시작마당을찍어시각무효(원본보존).12EXE는기능통과했어도staticAABB빈모서리가영웅과겹쳐보스를.32로흐리게하고terminaltick사망정지라시각보류. `full12/VISUAL-REJECTED.ko.md`,normal05소스GPU22PNG와RESULT-REVIEW(11과전투동일)를따른다. 기존11QA로그재사용fixture01이력은raw11증거불변과구분한다.

원본/파생은 `C:/Project/game-research/art-sources/oga-chained-demon-20261101-01/`에보존. motion02베이크12m실패,03/04수정과source초과가중치4개보정,material05원diffuse픽셀/면수유지3분리,자체FK8클립. 공개blend는항상Blender공식portable--disable-autoexec. Glutton둥근실루엣거절, SkeletonOutlawCC014모션nativeufbx변환/9clip미리보기(Atlasbasename복구)까지만/미채택, HorrorMonster작가preview만. D2/SACRATA보호자산미사용. `chapter1/art/QUALITY13-LEDGER.json`과출처MD/credits/PCK감사를따른다.

도감v06 `plans/chapter1-quality04-20261101-01/full13/book-v06/dist/index.html`9페이지(파수왕추가). 기존11의영웅/환경/장비페이지와09대연구05의24초영상은원번호로유지했다. 실제13GPU330초표지/배치와정상구분.1440desktop/390mobile9제목·탐색/가로폭18case확인,desktop표지/보스와mobile표지PNG. 초기BUILD/상태pending/HTMLrevision보존,REVISION02로최종로컬참조누락0. 모든offscreen이미지/영상/음향/인쇄승인아님. 소유탭2닫고viewportreset,8783서버는검수후정리한다. 기존탭1(oldlocalhost8768)은변경하지않았다.

다음은냉기/번개큰형태·실제빙결→파쇄,일반/정예동작,공간깊이,장비스크롤/고유발견/보스사망→보상리듬이다. 실제nonempty보관함재시작/경쟁구간/수동5–8분/실청취/최종1080p3회는열림. 다음FX연구는full13freeze를고정하고별도stage에서시작한뒤검증후새후보로묶는다. 보호자산복사·커밋·업로드·구매없음. agents미사용/root단독. 기존증거동일출력재실행/루트전체editorimport금지.

아래 이전 본문은 exact bytes suffix로 보존했다.

---

'''
history={}
for name in ['HANDOFF.md','chapter1/FULL-CHAPTER.ko.md']:
 p=ROOT/name;old=p.read_bytes();dest=BACK/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(old)
 p.write_bytes(prefix.encode('utf-8')+old);assert p.read_bytes().endswith(old)
 history[name]={'old_sha256':sha(dest),'new_sha256':sha(p),'exact_old_suffix':True}
write(OUT/'HANDOFF-PRESERVATION.json',{'backup':str(BACK),'files':history})
write(OUT/'DELIVERABLES.json',{'build':read(OUT/'build/build.json'),'status':str(OUT/'STATUS.ko.md'),'book':str(BOOK/'index.html'),'gpu_first_victory_seconds':read(OUT/'GPU-FULL-RESULT.json')['result']['tick']/60,'goal':'active','artifact_hashes':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p)for p in [OUT/'STATUS.ko.md',OUT/'SACRATA-COMPARISON.ko.md',OUT/'GPU-FULL-RESULT.json',OUT/'FINAL-PRESERVATION.json',OUT/'HANDOFF-PRESERVATION.json',OUT/'book-v06/REVISION-02.json',ROOT/'chapter1/art/QUALITY13-LEDGER.json']}})
print(json.dumps({'book_local_refs':len(refs),'missing':missing,'source13_matches':True,'handoff_preserved':True,'goal':'active'}))
