# 2026-10-31 현재 상태 — 새1장 C2 후보02 플레이테스트 인수

성장·장비·군중·정예가 연결된 별도 전투를 구현하고 새 실행본 후보02를 내보냈다. 현재 실행은 `builds/chapter1/chapter1-c2-candidate-20261031-02/AshenCloister-Chapter1.exe`, SHA256 `111c8434bd13d9724a4b1551fce97d0d1d241d59cde92a7df4ee23909f111188`. 상세는 `plans/chapter1-c2-20261031-01/STATUS.ko.md`다. 코어03/패키지02를 구분한다.

독립 코어 기능75/경계114 actual0·의도76 actual1, 일반6입력5승1패(actual1,냉기seed71 64.9초 패배)를 보존했다. 후보01에서 발견한 HUD/도구주입 단축키 호환을02에서 수정했고 독립뷰53 actual0·의도54 actual1 및 부모 실제 OS 입력으로 확인했다. source42/PCK78, 원본/staging/EXE·과거source51/사용자저장 선택 핀을 별도 보존 결과에 연결한다.

부모 실기02:1440×810 메뉴/성장·무기/부적 비교장착·모달정지·좌클릭이동·Space/M안내·화염진화·3기술·실제57.433333초/499처치/Lv9/장비4개 패배HP0·재도전HP120·actualexit0. OS정예승리·실청취·WASD물리hold·별도초점상실은 미검수다. 후보01 자동승리와1080p p95약20ms를02 정식성능으로 바꾸지 않는다.

현재 도감 v02 `book-v02/dist/index.html`은17목차·39브리프·14실행이미지·실제PNG원장을 제공한다. v01은 보존했다. 부모 데스크톱 시각검수와 정적참조 검증을 연결하며 새모바일/전체메모·인쇄 재검수는 아니다. 미리보기 서버는 종료했다.

**C2 최종 품질과5–8분 1장 전체는 미완료다.** 독립2.5D 후보의 다른방향 행동·idle·환경소품·바닥반복·연속 타격/음향·성능을 개선한다. 연결3구역·이벤트·고유보스·보상보존·저장도 남았다. 새 C2는 저장을 구현하지 않았고 기존 equipment-v1/progress-v1을 읽거나 변경하지 않는다. 1장 품질 검수 전2·3장으로 확장하지 않는다.

이전 문서 bytes를 아래 exact suffix로 보존한다. 백업은 `C:/Project/game-research/implementation-backups/chapter1-c2-docs-before-20261031-01/`, 비교는 새C2 `FINAL-PRESERVATION.json`. 과거 기술 승인을 최종 아트/손맛 승인으로 해석하지 않는다.

---

# 2026-10-31 현재 상태 — 분석/제작 도감 기준선 · 성장 코어 구현

최신 문서 plans/chapter1-preproduction-20261031-01/{SACRATA-ANALYSIS.ko.md,PREDEVELOPMENT-GATE.ko.md,IMPLEMENTATION-REPORT.ko.md}. 도감 book/dist/index.html:14목차·39항목·25관찰장면. 분석은 대표 런/공식/코드 근거의 목표 수립 기준선이며 청취·전체 원작 검증은 아니다.

새 chapter1 성장 코어/3계열4랭크·진화 정의 구현, 정상actual0·의도적actual1. 월드·UI·최종 자산과 미통합. 기존 제품/실행본/저장 유지. 대표90초와5–8분1장 품질은 아직 미완료다.

---

# 2026-10-31 현재 상태 보완

1장5–8분 초안 유지·새 구현 미착수. D2 Survivors 직접 조작 관찰을 추가했으나 SACRATA 영상은 부분 분석이다. C0 영상 잔여 검토를 다시 열었으며, 전체 영상/음향 분석 또는 품질 승인 완료로 표시하지 않는다. plans/chapter1-replan-20261030-01/SACRATA-VIDEO-REVIEW.ko.md 및 BROWSER-PLAY.ko.md를 우선한다. 다음 제품 검수물은 실제 아트·성장·장비·군중 처리의90초이며 최종 범위는1장 전체다.

---

# 최신 제품 상태 — 1장 품질 재계획

2026-10-30. 기존 1–6단계와 7단계 기술 검증 이력은 보존한다. 사용자 실제 실행 피드백에 따라 현재 제품 품질은 목표 미달이다. 다음 구현의 기준은 `plans/chapter1-replan-20261030-01/CHAPTER1-PLAN.ko.md`와 `PLAYER-QUALITY-GATES.ko.md`다.

계획 재점검 완료/새 구현 미착수. 첫 장의 성장·파밍·군중 전투·정예/보스·아트/음향·재도전이 함께 통과한 후 2·3장으로 확장한다. 과거 기술 관문 통과를 최종 게임 품질 승인으로 사용하지 않는다.

사용자 확정 범위: **5–8분의 밀도 높은1장**, 주 참고작 **d2survivors.lol**. 10–15분 가정과 다른 동명 프로젝트의 주 참고 지위는 폐기했다. 실제 브라우저 플레이 확인은별도관찰로기록한다.

---

# 최신 상태 — 7단계 원정 기술 구간 승인

2026-10-30, Asia/Seoul. 부모(root)가 1–6단계 기술 관문 완료와 7단계 원정 기술 구간 완료를 확정했다. 아래 과거 진행표보다 이 상태와 `evidence/phase7/ROOT-ACCEPTANCE.ko.md`를 우선한다.

| 범위 | 현재 상태 |
|---|---|
|1–5단계|기존 승인·소스/실행본·성공/실패 원시 보존|
|6 드롭·성장|기술 승인 완료. 사망1회 보상·분리RNG·UID/epoch/generation·XP/획득·전체원자적profile·GPU/실제입력 완료|
|7 짧은 원정 기술 구간|구현·독립검증·코드검토·전용패키징·일반조건240초victory·2해상도GPU각38checks·300적성능3회·600초진단·실제OS패배/재도전·저장/로드 완료|
|7 최종 표현/사람 평가|KayKit/합성음 기술판. SACRATA 최종 아트·움직임·음향 청취·사용자 재미는 별도 미평가/잔여 제작 영역|

실행본은 `builds/phase7/phase7-candidate-20261030-01/AshenCloister-phase7.exe`, SHA256 `5a56ccb5a13973a7d223d5d4a71b75a0c51ad89db6c78b564c1b10b4c09c6f29`다. 실행·조작·loadclock0/R회복 의미는 `RUN.ko.md`를 따른다. 원본51/staging51/동일EXE/PCK104/6archive32/841guard·사용자파일·게임0 최종 대조는 `evidence/phase7/FINAL-PRESERVATION-CHECK.json`이다.

300적 합성 부하 p95는15.880/15.425/15.368ms이며 p99·최악·관찰 캡처 지연도 원시에 보존했다. 고정60FPS·동시300적+32loot 최대 부하·누수0·500적/300탄 통과로 해석하지 않는다. OS는 QA 직접/root 문서 확인이며 경로 격리 저장이다. 원작 연구 이미지는 원정 패키지에서 제외했고 workspace 원본은 유지했다. 모달 같은sim tick 반복 장착 cue 억제는 P3 표현 한계다.

승인 갱신 전 원문은 `C:/Project/game-research/implementation-backups/phase7-acceptance-docs-20261030-01/`에 보존했다. 아래는 이전 원문 전체다.

---

# 최신 단계별 구현 상태 — 6단계 승인, 7단계 준비

2026-10-30, Asia/Seoul. 부모(root)가 1–6단계 기술 관문 완료를 승인했다. 아래 과거 진행표와 미착수 문구보다 이 요약과 각 단계 승인 문서를 우선한다. 기존 본문은 역사 기록으로 전부 보존했다.

| 단계 | 현재 상태 | 근거/다음 관문 |
|---|---|---|
| 0–5 | 완료·기술 승인 유지 | 각 단계 ROOT-ACCEPTANCE와 보존 source/EXE/실행 증거 |
| 6 드롭·성장 | 완료·부모 기술 통합 승인 | 독립core255/씬54·negative actualexit1·기존회귀/bitwise59·코드검토·동일후보정식GPU3회·외부QA각52·보조담당 실제OS입력. `evidence/phase6/ROOT-ACCEPTANCE.ko.md` |
| 7 짧은 완성 구간 | 계약 초안 준비·제품 미착수 | `evidence/phase7/PREP-20261030-01/CONTRACT-DRAFT.ko.md`와 근거JSON. 새단계백업 후 구현→독립검증→코드검토→실제실행 |

6단계 동결제품32개/실행본은 candidate01, EXE SHA256 `8f787d8d043951e0d500743f38c3df1348dfadb99a08f04365b36310ba38ab89`다. 실제1080p/Forward+/300적·3장비·3스킬/10초warmup+60초×3 p95는13.983/14.111/13.799ms로 각exit0. 조건과 한계는 `evidence/phase6/MEASUREMENTS.ko.md`를 따른다. ground32는 별도약8초진단으로 한정한다. 최종32/EXE·이전5단계보존27/EXE·변경전100백업·과거87guard·사용자파일보호의 서로 다른 범위는 `evidence/phase6/FINAL-PRESERVATION-CHECK.json`에 있다.

실제 OS입력은 보조담당자의 직접관찰이고 root는 기록을 확인했다. 기존 사용자equipment SHA는 `b376f88d6db4c443332908f5cf09860a4eda24701cbefb25c9cbd8289e202353`로 유지했고 native progress는 전후absent다. 실제UI저장은격리경로를썼으므로 기본native경로 저장입증으로 해석하지 않는다. 이번승인은 최종SACRATA아트/재미·고정60FPS·500적/300탄·누수0이 아니다. 과거phase3보조보고서2개복구미입증한계는 계속유지한다.

승인갱신전원문6파일은 `C:/Project/game-research/implementation-backups/phase6-acceptance-docs-20261030-01/`에 보존했다. 아래는 이전본문 전체다.

---

# 단계별 구현 상태

2026-10-30 인계 갱신. 사용자가 단계별 구현·검증 후 다음 단계로 계속 진행하도록 승인했다. 1–5단계 기술 관문을 부모가 승인했고 6단계 인수를 시작한다. 이 갱신 시점의 6단계 제품은 아직 미착수다. 최신 인계는 `HANDOFF.md`를 읽는다.

## 실행 기준

- 계획: `C:\Project\game-research\plans\2026-10-26-godot-d2r\DEVELOPMENT-PLAN.ko.md`
- 모델: 같은 폴더 `DATA-MODEL.ko.md`
- 엔진: Godot4.5.1 / GDScript / 기존 프로젝트 유지.
- Git 저장소가 아니므로 커밋·푸시는 하지 않는다. 단계별 백업·manifest와 증거로 보존한다.
- REA 사실, CASC 원문, 클래식 참조, 원작 관찰, 독립 설계값을 구분한다.
- 전체 D2R 네이티브 복원과 SACRATA 품질을 완료했다고 표시하지 않는다.

## 진행표

| 단계 | 상태 | 근거/다음 관문 |
|---|---|---|
| 0 현황·문서 조사 | 완료 | 분석 보고서와 CODE-INTEGRITY.json |
| 1 독립 데이터 계약 | 완료·root 승인 | canonical catalog/transactional loader/호환 어댑터/HUD. 기존40/109·새62·독립320·Python2 통과 및 negative exit1, 실제GPU/최종EXE QA. root가화면·report·EXE SHA 확인 |
| 2 다중 개체 | 완료·root 승인 | 기존40/109/62/320·core203/실제씬53·Python2/import 통과 및 negative exit1. 별도 코드검토/실제GPU 소스1·10·100/최종EXE0·1·10·100/실제UI 입력 확인. evidence/phase2/ROOT-ACCEPTANCE.ko.md |
| 3 군중 성능 | 완료·root 기술 통합 승인 | 현재 대역 아트/현재 스킬 밀집300리그/표현 LOD/고HP마나fixture 범위. 1080p·60초×3·600초·독립 감사/재현·코드 검토·일반EXE QA/실제UI 확인.500적·300탄미달 및메모리잔차·최종품질미평가한계공개. evidence/phase3/ROOT-ACCEPTANCE.ko.md |
| 4 전투·스킬 | 완료·부모 기술 통합 승인 | 제품 22개 동결, 독립 기능·금지 패턴·코드 검토, 실제 1080p·300적·3스킬 순환 60초 × 3회 및 독립 감사/재현, 최종 EXE 일반 QA 6건·부모 실제 입력. `evidence/phase4/ROOT-ACCEPTANCE.ko.md` |
| 5 아이템·옵션 | 완료·부모 기술 통합 승인 | 독립 장비3종·개별옵션/UID/RNG·장착/해제·요구 조건·화염탄 보너스·저장·I 모달. 동결27개/기능336·68·90·48·negative/코드검토/정식GPU3회·독립감사/재현/EXE QA두해상도/부모실제입력. `evidence/phase5/ROOT-ACCEPTANCE.ko.md` |
| 6 드롭·성장 | 인수 시작·제품 미착수 | 사망1회 보상1회, 별도 loot RNG·독립 드롭/XP/획득·장비 연결·저장 복원 중복 방지 |
| 7 짧은 완성 구간 | 미착수 | 대표 아트·입력·최종 성능/연속 실행 검증 |

현재 단계의 테스트 수는 검사 분기 수이며 원작 규칙 수나 재미·최종 아트 품질의 증명이 아니다. 후속 단계는 직전 단계의 구현·독립 검증·리뷰를 확인한 뒤 시작한다.

보존된 4단계 최종 EXE는 `builds/phase4/phase4-candidate-20261029-02/D2RCombatBaseline-phase4.exe`, SHA256 `5577230ecaec6a2f1461931dcd44551c77fbf9a33153e71a56368bcd96d42067`다. 다중 스킬 300적 p95는 13.666 / 14.020 / 13.185 ms, 독립 재현 13.269 ms다. 동시 감속 최대12개·잔존 비행탄 최대0개인 밀집 합성 부하이며 고정60FPS, SACRATA 품질, 재미, 500적·300탄 극한 부하, 메모리 누수0을 승인한 것이 아니다. 이월된 자동 시전 버튼/설명 겹침은5단계에서 두 해상도 GPU QA와 부모 기본 화면 관찰로 해소를 확인했다.

5단계 승인 EXE는 `builds/phase5/phase5-candidate-20261029-01/D2RCombatBaseline-phase5.exe`, SHA256 `92b502172ddbeed5c8c55f21d97f772c21b11a38cde41673f5e59ecbf90ae20e`다. 실제1080p·장비3개·300적·3스킬·워밍업10초·60초×3 p95는14.057 /13.213 /13.174ms, 독립 재현13.542ms다. 실제 사용자 저장을 새로 생성해 원본과 복사본 SHA를 보존했다. `evidence/phase5/ROOT-UI-OBSERVATIONS.ko.md`, `FINAL-PRESERVATION-CHECK.json`과 `root-native-save/manifest.json`을 따른다. 6단계 변경 전 이 소스 snapshot/EXE와 현재 사용자 save를 보존한다. 이후 현재 소스 변경을5단계 승인 실패로 오인하지 않는다.

**보존 사고:** 기존 씬 검사 출력 경로를 분리하지 못해 phase3의 `scene-regression-report/scene-run.json`과 `mixed-corpse-report/scene-run.json` 두 보조 보고서가 다시 작성됐다. 이전 바이트 복구는 입증되지 않았고 현재 파일을 과거 승인 원본으로 인용하면 안 된다. `evidence/phase4/EVIDENCE-PRESERVATION-INCIDENT.ko.md`와 `evidence/phase3/PRESERVATION-NOTE-20261029.ko.md`를 읽는다. 소스·EXE 핀 일치와 주요 GPU 원시 파일 존재 확인은 원시 전체 바이트 불변 입증과 다르다.

## 보존과 병행 조사

- 변경 전 백업: `C:\Project\game-research\implementation-backups\phase1-20261026`
- 새 1단계 증거: `evidence/phase1/`
- 1단계 구현 인계: `evidence/phase1/IMPLEMENTATION.ko.md`, 최종 EXE `builds/phase1/D2RCombatBaseline-final.exe`, SHA `a8b683938cf2a778b2a8838cde22aa3d95dee8a2ef15910e8e69a4aaaf75f4f5`.
- 원래 `evidence-profile.json`과 과거 증거는 보존한다.
- 2단계 변경 직전 보존: `C:\Project\game-research\implementation-backups\phase2-continuation-20261027-implementation`; 최종 소스: `phase2-final-source-20261027`; 승인 전 인계 문서: `phase2-acceptance-docs-20261027` (각 manifest 포함).
- 2단계 증거: `evidence/phase2/IMPLEMENTATION.ko.md`, `INDEPENDENT-REVIEW.ko.md`, `CODE-REVIEW.ko.md`, `ROOT-ACCEPTANCE.ko.md`. 최종 EXE `builds/phase2/D2RCombatBaseline-phase2.exe`, SHA256 `AA1CD5209ED713961A63895979DFDB8C1283AF9643DC7EC12B4E02F46FAC8331`.
- 100마리의 짧은 기능 실행은 성능 통과가 아니다. 실험 AI의 즉시 포위 사망을 재미·밸런스 수용 판정으로 취급하지 않는다.
- P0 스탯 조사: `C:\Project\game-research\d2r-analysis\research-p0\STAT-DEPENDENCIES.ko.md` 및 JSON.
- P0에서는 새 네이티브 분석을 하지 않았다. property→stat 연결은 로컬 표 근거다. 모든 stat의 scale이256이라고 원작 사실로 일반화하지 않는다. 아이템 화염 피해와 주문 mastery를 구분한다.

## 군중 표현 준비 조사

현재 Skeleton_Minion은9 mesh/2material/41joints다. 과거300개 Forward+ p95는30.889ms, 마지막 drawcall8238이며 현 검증판 결과가 아니다. 후보 순서는 공유재질/정적 batching → mesh/material별 부품 병합과 시간 기반 animation LOD → 필요할 때 near full-rig + far baked pose/VAT 표현 비교다.

공식4.5의 `bake_mesh_from_current_skeleton_pose()`는 skin/skeleton 필요, material 미복사, GPU readback stall 경고가 있다. 오프라인/시작 시 제한된 pose 캐시 후보이며 매 프레임 수백 번 사용하지 않는다. MultiMesh는 개별 culling이 없고 instance custom data 정밀도는 Compatibility16bit/Forward+32bit다. 실제 심·표시·full-rig·batch 개체 수를 구분해 기록한다. 이 내용은 아직 미구현 후보이고 실제300개/60FPS 증거가 아니다.

3단계 계측 API 준비: 공식 Godot4.5 RenderingServer 문서에서 `viewport_set_measure_render_time(viewport RID, true)` 뒤 `viewport_get_measured_render_time_cpu/gpu(viewport RID)`로 ms를 읽는 경로를 확인했다. CPU render 값에는 scripts/process 등 다른 subsystem이 포함되지 않는다. CPU 렌더 전체는 viewport 합과 `get_frame_setup_time_cpu()`를 구분해 기록한다. `viewport_get_render_info()`는 최소2프레임 뒤 사용한다. headless는 RenderingServer dummy값이므로 실제GPU측정으로 쓰지 않는다. 사용 여부/renderer지원/0값은 실제실행에서 확인해야 한다.

공식 출처: https://docs.godotengine.org/en/4.5/classes/class_renderingserver.html#class-renderingserver-method-viewport-set-measure-render-time

## 과거 3단계 WIP 갱신 — 현재 상태 아님
최종19제품 소스는 독립 기능 검증·코드 검토 후 release EXE로 내보냈다. 2026-10-28 재개 시 동일성을 다시 확인했다. 최종 release matrix 일부와10분soak/최종실행 승인 관문은 미완료다. 자세한 현재 상태는 evidence/phase3/RESUME-20261028.ko.md를 우선 읽는다. 4–7단계는 미착수다.

