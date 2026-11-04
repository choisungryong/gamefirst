from pathlib import Path
import json,hashlib,shutil
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';OUT=B/'full17b/finalization01';assert not OUT.exists();OUT.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
gpu=read(B/'full17/runtime/gpu-cold01/RESULT.json');execution=read(B/'full17/runtime/gpu-cold01/gpu-execution.json');assert execution=={'actual_exit':0,'stderr_bytes':0};assert gpu['observer']['epoch']==1 and gpu['observer']['shatters']==840 and all(gpu['same10_as_packaged16'].values())
freeze=read(B/'full17b/FINAL-SOURCE-FREEZE.json');assert all(sha(R/n)==h for n,h in freeze.items())
build=read(B/'full17b/build/build.json');assert sha(Path(build['exe']))==build['sha256']
pins={}
for version in ['14','16','17','17b']:
 p=Path(read(B/('full'+version+'/build/build.json'))['exe']);pins[str(p)]=sha(p)
 assert pins[str(p)]==read(B/('full'+version+'/build/build.json'))['sha256']
old=(R/'HANDOFF.md').read_bytes();(OUT/'HANDOFF-before.md').write_bytes(old)
summary=f'''# 최신 인계 — 2026-11-02 / 후보17b 경계 수정까지 진행 / 목표 미완료

먼저 `plans/chapter1-quality04-20261101-01/full17b/STATUS.ko.md`, `full17/runtime/gpu-cold01/RESULT.json`, `full16/OLD-CHAT-INFLIGHT.ko.md`를 읽는다. 이전 창은 사용자가 일시중지했으며 이 창이 후속 작업을 담당한다. 아래 과거16미패키징/17이전상태는 역사기록이다.

## 현재 실행본과 보존

- 최신개발EXE는후보17b `builds/chapter1/chapter1-full-candidate-20261102-17b/AshenCloister-Chapter1.exe`,SHA `{build['sha256']}`,{build['bytes']}bytes/runtime107/stage109/PCK192. 루트조립은16 core/FX +17HUD/Actor/World이고World17파일의배치상수만17b다. rootmain/preset은Baseline유지.
- 후보14·16·17 EXE/stage/freeze와성공/실패/사용자저장보존.16전체루트소스백업 `C:/Project/game-research/implementation-backups/chapter1-before17-20261102-01/`.17원World는full17b/world17-before-boundary.gd와보관17stage.14/16/17/17b해시는full17b/finalization01/RESULT.json.
- 독립감사17은40항목:14/16/17stage·EXE·root17freeze(당시)·전체16백업·30headless상태/PCK/nativequiet. 이후World배치수정으로현재root는17bfreeze와맞고17freeze와는World만다르다.17b독립감사13항목모두true. 선택과거핀검증이지모든역사바이트/모든사용자저장전수감사가아니다.

## 기존GPU16은 끝났고 재실행하지 않음

- full16/runtime/gpu-cold01:engineexit0/stderr0,첫/최종epoch1victory23862tick/3451kill/Lv12,패키지headless10상태동일.24PNG.게임승리는유효하다.
- observerepoch-1/shatter1/cold0통계는무효이고helper최종assert실패다.RESULT.json을성공처럼재작성하지않았다.별도gpu-cold01-review/RESULT.json에분리했다. 원시스크립트/로그/실패그대로다.

## 새17 표현 변경과 실제 검수

- Actor17:일반·중간정예의기존4프레임이동위상을ID별분산,실제windup/dash에작은기울기.새골격/방향별공격아트완성아님.영웅/73골격파수왕은기존경로.
- HUD17+EquipmentSigil17:선택재구성후스크롤유지,슬롯문양/희귀도색/고유설명.실제보상UID유산카드,승리후1.3초세계표시로기존1.125초보스죽음을먼저보여줌.피해/장비수치/지급/저장규칙그대로.
- World17:기존돌질감을쓴114기단/팔각기둥/낮은석재,6MultiMesh배치.새외부아트없음.원17은일부보행범위안에놓인문제로공간배치보류.17b는기둥|z|21.4/낮은석재22.8로옮김.실제17bGPU경계fixture에서모든코너최소|z|20.4966>보행19+여유.8,6배치/114석재,exit0/stderr0.영웅z19직접배치fixture이지정상한판아님.
- presentation17/review04:정상정책54초/첫승리직전core재구성뒤짧은GPU.전투/종료전체core전후시작·끝동일,scroll650유지/고유설명/사망전세계표시/보상표시4검사true/quiet.실패01(보상필드),02(scroll/회색블록),03(석재면)보존.04baseline은03before16을재사용.
- full17/runtime/native-gear01:실제EXE정상획득34개빌드재구성후네이티브휠/반지선택/장착/I복귀/AltF4확인.목록위치유지/장착◆/최대HP176→188(현재147유지)/고유보상복귀,exit0/stderr0。profile-off,수동전체나저장UI검사아님.
- **full17 실제 패키지 전체GPU 종료 확인**:397.7초/23862tick/3451kill/Lv12,실제observerepoch1/파쇄{gpu['observer']['shatters']}회/냉기직접처치원인{gpu['observer']['cold_death_cause']}회,16과10게임상태동일,exit0/stderr0/{gpu['captures']}PNG.외부observer는짧은65simsec headless사전검사에서epoch1/39파쇄를확인후전체GPU에사용.첫승리후2.1초정상종료.게임/패키지17을전체GPU라부르고17b전체로확대하지않는다.
- 세주력17전체headless는화염362.4833초/3185,냉기397.7초/3451,번개376.1333초/3380으로16과각10상태동일.17b는World의배치상수만달라전체행렬상속을명시하고중복실행안함.17b는별도30초release/출처PCK/경계GPU만새로했다.

## 에셋북과 다음 작업

- v08(12페이지/227refs missing0)보존,11nav페이지1440/390폭22case,h1/overflow통과,6초비교영상끝재생확인.초안book_cold16.py문자열SyntaxError보존,02로생성.
- v09(14페이지/282refs missing0)보존,12nav페이지1440/390폭24case통과.17연구와16패키지GPU/observer실패구분.후속v10은full17b/book-v10/dist/index.html로17전체GPU와17b경계수정을구분한다.최종브라우저검수문서는book-v10/REVIEW.ko.md를확인한다.
- **다음우선순위**:경계카메라에서바닥평면끝/빈배경삼각영역이보이는문제를고치고자연스러운공간구성확인.일반/중간정예는4프레임위상/기울기보완뿐이라실제풍부한동작/실루엣은미완료.고유발견카드는현재일반정책에서고유가최종보상으로만생기므로playing발견연출의실전승인으로세지말것.보스보상은실제전체GPU화면을보고추가리듬개선.
- 수동5–8분전체/실제음향청취/네이티브보관함재시작UI/최종1080p3회성능은미완료.첫장목표active,기술검사/도감으로완료판정금지,2·3장확장금지.기존런/출력/EXE를덮어쓰거나같은GPU중복실행금지.항상새격리stage/output.
- HTTP서버는book-v08/browser01/server.pid.txt의로컬8781서버다.게임프로세스는종료후실제확인하고,서버를정리하면도감탭localhost가끊기는점을구분한다.

---

## 이전 인계 원문 (exact bytes suffix)

'''
(R/'HANDOFF.md').write_bytes(summary.encode('utf-8')+old)
for folder,update in [('full17',f'# 최종 실행 갱신\n\n후보17 실제 패키지GPU:397.7초/3451처치/Lv12/파쇄840(냉기직접원인{gpu["observer"]["cold_death_cause"]}),epoch1/exit0/stderr0,16과10상태동일/{gpu["captures"]}PNG.세주력headless/네이티브UI검사도성공. 단공간배치는보행범위안기둥문제로보류해17b로수정했으며17을최신배치로추천하지않는다.원17EXE/소스/실행보존.\n\n'),('full17b','# 최종 실행 구분\n\n17 전체GPU는종료0/stderr0/397.7초/3451처치/파쇄840/냉기직접원인823이다.17b는동일HUD/Actor/core/FX이고World배치상수만수정한별도EXE다.17b자체전체GPU나수동완료로세지않는다.경계GPU/출처감사13검사성공.아래남은품질관문을계속한다.\n\n')]:
 p=B/folder/'STATUS.ko.md';shutil.copy2(p,OUT/(folder+'-STATUS-before.md'));p.write_bytes(update.encode('utf-8')+p.read_bytes())
report={'build17b':build,'preserved_exes':pins,'root17b_freeze_match':True,'gpu17_execution':execution,'gpu17_counts':gpu['observer'],'handoff_old_sha256':hashlib.sha256(old).hexdigest(),'handoff_exact_suffix':(R/'HANDOFF.md').read_bytes().endswith(old),'goal_complete':False}
(OUT/'RESULT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False),flush=True)
