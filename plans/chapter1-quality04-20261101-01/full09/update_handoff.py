from pathlib import Path
import hashlib,json,shutil
ROOT=Path('C:/Project/d2r-combat-baseline');HERE=Path(__file__).parent
backup=Path('C:/Project/game-research/implementation-backups/chapter1-full-handoff-before-20261101-01');assert not backup.exists();backup.mkdir()
files=['HANDOFF.md','plans/chapter1-quality04-20261101-01/WIP-HANDOFF.ko.md']
old={p:(ROOT/p).read_bytes() for p in files}
for p,raw in old.items():
 target=backup/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
with (backup/'manifest.json').open('x',encoding='utf-8') as f:json.dump({p:hashlib.sha256(b).hexdigest() for p,b in old.items()},f,indent=2)
head='''# 2026-11-01 최신 — 전체1장 후보09 실행 · 목표 active

먼저 `plans/chapter1-quality04-20261101-01/full09/STATUS.ko.md`를 읽는다. 이제 대표90초 외에 세 마당/두 회랑·봉인·선택의식2·정예2·보스2단계·회복약·장비12base/12affix/3unique·새 전용 보관함/저장을 연결한 **별도 전체1장 기능 분기**가 있다. 품질 관문을 통과한 것으로 해석하지 않으며 목표는 active다. SACRATA 수준의 동작·환경·타격/음향, 수동 한 판·실청취·정식 성능은 계속 개선한다.

최신 실행: `builds/chapter1/chapter1-full-candidate-20261101-09/AshenCloister-Chapter1.exe`,116595376bytes, SHA `98ead9b666373b1e746d8c57910c8ee27265290b78c0c01e35c9e268ad358724`, runtime83/stage85/PCK146. 소스 루트main은 기존 Baseline 그대로, 이 패키지main은 `chapter1/ChapterOne.tscn`이다. 후보07/08과 이전C2/phase7 실행·실패·증거를 모두 유지한다.

후보09 실제 release/headless/fixed60 정상 입력은 화염362.4833초/3185kill/Lv11, 냉기427.8667초/3779/Lv12, 번개376.1333초/3380/Lv12 모두 실제 승리/주력진화/고유 보상 소유, actual0/stderr0이다. 실제GPU 자동 입력 화염도21749틱/6분2초 동일 완료,23PNG, 종료0/stderr0. root가 CUA로 승리/보상목록/잿꽃의 유언 비교(-10%피해/+1발사체/처치폭발)를 확인했다. 마지막 장착 클릭은 자동 종료 이후라 성공 미확인. 수동 전체완료·실청취·정식성능 승인은 아니다.

후보07은 assert 내부의 실제 선택/장착/import 호출이 release에서 생략돼 첫 선택에 멈췄다.08에서 수정했으나 고정FPS 종료 오디오 경고가 나왔다.09는 종료 요청 후 물리 정지와150ms 실제 audio release 대기. 원시 실패/verbose/WAV 목록과 EXE는 보존했다. release EXE 외부 동작fixture7, C2 semantic75/crowd48, 전체코어49(장비12000roll), 새profile27 통과. negative실제1도 보존했다. source09 freeze와 baseline51/backup77/과거EXE3·사용자저장2/oldstage72 선택 핀 일치. 옛 모든sidecar 불변 주장은 하지 않는다.

도감 v04: `plans/chapter1-quality04-20261101-01/full09/book-v04/dist/index.html`,6페이지/현재GPU 이미지/장비표/보관함/리깅연구/검증.69로컬 링크누락0, desktop6제목·표지/장비/연구화면 확인. 첫 이미지 넘침은CSS수정/재확인, 원초안/BUILD/REVISION-02 유지. 모바일/인쇄미검수. 임시탭6과 localhost8779 서버 정리. 원 사용자YouTube탭1은 그대로다. 옛 임시탭3 제어불가 한계는 이전 기록대로다.

실제 리깅 mage는 공개 CC-BY-SA3.0 연구 후보이며 아직 런타임 미채택. 공식Blender4.5.15 checksum 검증 portable 준비 완료. `C:/Project/game-research/art-sources/oga-mage-20261101-01/` 원본/파생blend/GLB/5clip/54엔진bones/Godot12PNG, 옷감stretch와단순사망이 남는다. Flare HD도 미채택. 반복 AI8보행03은 거절 보존. 새 model이 있다는 이유로 아트 완료 처리하지 않는다.

다음은 실제 SACRATA 연속 영상과 후보09의 흐름을 대응하고, 영웅·정예·보스 실동작/실루엣·반복 식생/평면 바닥·연속 타격/실제 믹스를 개선한다. 추가 기능/2·3장보다 이 품질 격차에 집중한다. 새 저장은 새 전용namespace만 사용하며 실제 nonempty보관함 재시작/다중 프로세스 경쟁구간/전원손실 검수와 목록 선택 시 스크롤초기화 불편이 남는다. Agents는 사용량 제한으로 중단되어 root가 직접 작업 중이다. 새 agents 반복 생성/루트 전체 editor import는 하지 않는다.

아래 옛 HANDOFF 본문은 exact bytes suffix로 보존했다. 상세 이전 C2 품질04는 WIP의 역사 부분을 따른다.

---

'''
for p,raw in old.items():
 prefix=head if p=='HANDOFF.md' else '# 최신 전체1장 후보09 진행\n\n`full09/STATUS.ko.md`와 루트 HANDOFF 최신 머리말을 우선한다. 아래 품질04 기록은 보존된 이전 상태다. 전체1장 기능분기/후보07–09/릴리스 결함·수정/새 도감/실제GPU6분2초 완료는 full09에 있다. 최종목표는 active다.\n\n---\n\n'
 (ROOT/p).write_bytes(prefix.encode('utf-8')+raw)
 assert (ROOT/p).read_bytes().endswith(raw)
with (HERE/'HANDOFF-PRESERVATION.json').open('x',encoding='utf-8') as f:json.dump({'backup':str(backup),'files':{p:{'old_sha256':hashlib.sha256(b).hexdigest(),'new_sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),'exact_old_suffix':True} for p,b in old.items()}},f,indent=2)
print('HANDOFF_FULL09_UPDATED')
