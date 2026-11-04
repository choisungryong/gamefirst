from pathlib import Path
import json,hashlib
R=Path('C:/Project/d2r-combat-baseline');B=R/'plans/chapter1-quality04-20261101-01';OUT=B/'full18/finalization01';assert not OUT.exists();OUT.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=read(B/'full18/FINAL-SOURCE-FREEZE.json');assert all(sha(R/n)==h for n,h in freeze.items())
build=read(B/'full18/build/build.json');matrix=read(B/'full18/runtime/ground-matrix01/RESULT.json');book=read(B/'full18/book-v11/BUILD.json');assert matrix['all_new_floor_covers'] and matrix['core_unchanged'] and not book['missing']
pins={}
for version in ['14','16','17','17b','18']:
 p=Path(read(B/('full'+version+'/build/build.json'))['exe']);pins[str(p)]=sha(p);assert pins[str(p)]==read(B/('full'+version+'/build/build.json'))['sha256']
old=(R/'HANDOFF.md').read_bytes();(OUT/'HANDOFF-before.md').write_bytes(old)
header=f'''# 최신 인계 — 2026-11-02 / 후보18 경계 바닥 수정 완료 / 첫 장 품질은 진행 중

먼저 `plans/chapter1-quality04-20261101-01/full18/STATUS.ko.md`, `full18/runtime/ground-matrix01/RESULT.json`, `full18/independent-audit01/RESULT.json`을 읽는다. 이전 창은 사용자 요청으로 일시중지 상태다. 기존16·17 GPU는 종료됐고 재실행하지 않았다. 아래 과거 인계의 “경계 바닥 빈 영역”은18에서 수정했으며, 공간 전체의 미술 품질 완료라는 뜻은 아니다.

## 현재 제품

- 최신 개발 EXE: `builds/chapter1/chapter1-full-candidate-20261102-18/AshenCloister-Chapter1.exe`, SHA256 `{build['sha256']}`, {build['bytes']}bytes/runtime108/stage110/PCK194.
- 루트 조립은 core16/FX16/HUD17/Actor17/World18이다. World18은17b 상태의 World17을 상속한다. root main/preset은 Baseline 그대로다.18은 별도 Quality18 저장 namespace이며 기존 저장을 옮기거나 변경하지 않았다.
- 14·16·17·17b·18 EXE와 각 stage/freeze, 성공·실패 원본을 보존했다.18 변경 전 root17b 조립/project/preset은 `C:/Project/game-research/implementation-backups/chapter1-before18-20261102-01/`에 보존했고 나머지17b 전체 소스는 보관 stage 핀과 대조했다.18의 기존 파일 변경은 chapter_one_view World preload 한 곳이며 새 제품 파일은 `chapter1/view/chapter_world_quality18.gd` 하나다.

## 이번 수정과 검수

- 기존 바닥160×70이 경계 카메라의 시야보다 작아 빈 배경 삼각 영역이 보였다. World18은 현재 viewport 네 모서리의 바닥 투영, 세 구역의 보행 가능한 카메라 타깃 외곽,3m 여유로 기존 PlaneMesh의 크기/중심만 조정한다. 같은 viewport·camera.size에서는 캐시한다. 기존 월드 좌표 셰이더/재질/충돌/코어/배치/노드 수는 그대로다. 바닥 surface1 유지.
- 소스 `ground18/matrix01`: 새 외부 최소 stage import/check/GPU exit0/stderr0.3구역×4모서리×3화면비(1440×810,1200×900,1920×540)=36경우 모두 새 바닥이 화면을 덮었다. 같은 투영에 기존 바닥 영역을 적용하면36경우 모두 일부가 밖으로 나간다. 코어 snapshot 불변.13PNG.
- **실제 패키지18** `full18/runtime/ground-matrix01`: 외부 bootstrap으로 패키지 제품 클래스를 사용해 같은36경우를 GPU 검수했다. 소스와36개 결과 행이 완전히 같고 모두 통과, exit0/stderr0/13PNG. 영웅을 경계에 직접 놓는 fixture이며 정상 한 판/수동/실성능이 아니다. 화면비 검수를 위해 content-scale을 껐으며 전후 전체 UI 픽셀 동일 주장을 하지 않는다.
- 실제17b hero(-4,19)의 실패 PNG를 재실행 없이 보존 참조했다.18 실제 패키지의 같은 위치에서 빈 삼각 영역이 흙바닥으로 이어지는 것을 직접 봤고, 바깥 모서리·4:3·32:9 화면도 확인했다. 바깥에 흙이 넓게 보이는 구도 자체는 추가 미술 개선 대상이다.
-18 패키지 export/PCK/리소스 load/30초 정상 정책/입력 정책 probe 성공. 독립 감사18항목은 root/stage/EXE/PCK,14/16/17/17b 보존, 테스트한 소스와 실제 패키지 일치, 원17b 조립 백업을 확인했다. 선택 과거 핀 검증이지 모든 역사 파일/모든 사용자 저장 전수 감사는 아니다.
- 전체3주력 headless/전체 냉기 GPU의6분37.7초/3451처치/파쇄840은 변경 없는16 core/17 표현의 **원17** 결과를 범위 명시해 상속한다.18 전체 정상 GPU를 새로 했다고 하지 않는다. 같은 전체 검사를 중복 실행하지 않았다.

## 에셋북과 다음 작업

- 최신 `full18/book-v11/dist/index.html`:16페이지/{book['local_references']}localrefs/missing0. 실제 브라우저에서16페이지×1440/390폭32case 제목/가로 넘침 통과, 새 표지·경계 페이지를 직접 봤다. `book-v11/REVIEW.ko.md` 참고. v08/v09/v10 원본과 원시 미디어 보존.
- 다음은 일반/중간 정예의 기존4프레임 동작 한계와 방향별 공격 실루엣, 바깥 흙/폐허의 자연스러운 공간 구성·깊이를 개선한다. 바닥 끝이 사라진 것을 전체 공간 미술 완성으로 간주하지 않는다. 현재 고유 장비는 정상 정책에서 최종 보상으로 생기므로 playing 발견 배너의 실전 승인을 주장하지 않는다.
- 수동5–8분 전체/실제 음향 청취/네이티브 저장UI/최종1080p3회 성능은 미완료. 첫 장 목표 active이며2·3장 확장하지 않는다. 기술 검사나 도감으로 SACRATA 지향 품질을 완료판정하지 않는다.
- 모든 이번 게임 실행은 terminal이다. 서버8781은 기존 `full16/book-v08/browser01/server.pid.txt`의 로컬 HTTP 서버이며 도감 산출물 탭을 위해 남겼다. 다음 재개 시 실제 PID/실행 상태를 확인한다. 기존 stage/output을 덮어쓰거나 같은 GPU를 중복 실행하지 않는다.

---

## 이전 인계 원문 (exact bytes suffix)

'''
(R/'HANDOFF.md').write_bytes(header.encode('utf-8')+old)
report={'build18':build,'preserved_exes':pins,'root18_freeze_match':True,'matrix36_same_source_and_package':matrix['cases']==read(B/'ground18/matrix01/RESULT.json')['cases'],'handoff_exact_suffix':(R/'HANDOFF.md').read_bytes().endswith(old),'old_handoff_sha256':hashlib.sha256(old).hexdigest(),'goal_complete':False}
(OUT/'RESULT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'latest':build['exe'],'preservation':True,'matrix':True,'book_pages':book['pages'],'goal_complete':False},ensure_ascii=False),flush=True)
