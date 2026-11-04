# 첫 전투 실행 후보 · C2 품질 검수 진행 중

2026-10-31, Asia/Seoul. **성장·장비·군중·정예가 연결된 실제 전투를 구현했다. 목표인 5–8분짜리 1장 전체와 SACRATA 목표 품질은 아직 완성하지 않았다.** 현재 실행본은 후보02이며 부모 직접 조작과 새 도감의 데스크톱 표시를 검수했다. 후보02는 플레이테스트용으로 인수했으며 C2 제품 품질 합격은 아니다.


- [현재 실행본02](C:/Project/d2r-combat-baseline/builds/chapter1/chapter1-c2-candidate-20261031-02/AshenCloister-Chapter1.exe) · [조작과 범위](C:/Project/d2r-combat-baseline/builds/chapter1/chapter1-c2-candidate-20261031-02/RUN.ko.md)
- [제작 도감 v0.2](C:/Project/d2r-combat-baseline/plans/chapter1-c2-20261031-01/book-v02/dist/index.html) · [직접 조작 원문](C:/Project/d2r-combat-baseline/plans/chapter1-c2-20261031-01/native-runtime-02/OBSERVATIONS.ko.md)
- [코어03 독립 검증](C:/Project/d2r-combat-baseline/plans/chapter1-c2-20261031-01/verification-core-03/REPORT.ko.md) · [패키지02 검증](C:/Project/d2r-combat-baseline/plans/chapter1-c2-20261031-01/package-candidate02/PACKAGING-REPORT.ko.md)

## 실제로 연결한 것

- 원소술사로 시작 기술을 선택하고 화염·냉기·번개를 각자의 주기로 자동 시전한다. XP 회수와 3지선다, 기술 4랭크·선행 패시브·진화가 전투에 반영된다.
- 추격·원거리·돌진의 일반 적 3역할과 정예 회랑 수호자가 각기 전조·공격·회복 상태를 갖는다. 70초에 등장하는 정예를 실제로 처치하면 즉시 승리한다. 시간만으로 승리하지 않는다.
- 무기·갑옷·부적·반지 4슬롯의 실제 드롭·회수·비교·장착을 연결했다. 장비가 피해·발사체/연쇄·파쇄·회수 반경·주기·최대 생명력/감소에 반영된다. 장착은 현재 생명력을 회복하지 않는다. 최종 1장 장비 pool 전체가 완성된 것은 아니다.
- 별도 `chapter1/Chapter1.tscn`과 fixed-tick 코어·표현자를 추가했다. 기존 Baseline/Expedition 진입점은 유지한다. 새 C2는 기존 저장을 읽거나 바꾸지 않으며 자체 저장 기능도 아직 없다.
- 독자 생성한 성인 비율 원소술사와 적 4종의 2.5D PNG 아틀라스, 가변 사각형·발 기준점 JSON을 사용한다. 각 역할은 이동 4방향×4키프레임과 남쪽 공격/시전·피격·사망 각 4키프레임을 갖는다. 리깅 3D가 아니다.
- 발사체 shader·화염 충격·서리/빙결·연쇄·XP/장비·위험 전조와 발 그림자·주인공 위치 표시를 연결했다. 메뉴·성장·장비·정지·승패·재도전 UI가 있다. 현재 소리는 기존 독자 합성 WAV와 bounded 재생 관리자를 재사용한다.

## 코어03 독립 검증

`verification-core-03/REPORT.ko.md`에 명령·실제 종료 코드·정상 입력 원시 결과를 연결했다.

| 확인 | 실제 결과 |
| --- | --- |
| 기능 fixture | 75검사, actual exit0 |
| 의도적 실패 | 76검사, actual exit1 |
| 독립 경계 fixture | 114검사, actual exit0 |
| 3시작 기술×2seed 정상 입력 | 승리 5회·패배 1회, actual exit1 / success:false |
| 현재·보관 코어 의존성 | 9파일 pin, 검증 전후 불일치0 |

냉기 seed71은 64.9초/237처치/HP0/레벨10, 주력 진화와 기술 3개·장비 6개 상태에서 패배했다. CPU 소요 시간 외 결과 전체가 구현 담당 결과와 동일하게 재현됐다. 자동 입력도 패배할 수 있으므로 이 결과만으로 모든 사용자가 불가능한 빌드라고 단정하지 않는다. 동시에 정상 6사례 완주나 냉기 밸런스 승인을 주장하지 않는다. HP·XP·아이템·스폰·처치 주입 없이 실제 이동/회피·제시 카드 선택·소유 장비 장착만 사용했다.

바닥 아이템32개에서 정예 보상을 잃던 결함은 수정했다. 일반 소지품64개에 목표 보상 전용1칸을 두어 총65개로 제한하며 기존 장비/UID를 교체하거나 삭제하지 않는다. 사망 중복 지급·승리 후 실제 비교/장착과 회피 12회 이동·미래18step 무적/180tick 재사용 경계도 독립 실행했다. 코어02 실패와 코어03 변경·재검증 원시는 모두 보존했다.

## 현재 실행본02 검증

- 실행: `builds/chapter1/chapter1-c2-candidate-20261031-02/AshenCloister-Chapter1.exe`.
- EXE109675984bytes, SHA256 `111c8434bd13d9724a4b1551fce97d0d1d241d59cde92a7df4ee23909f111188`. source42/stage44/PCK78, 새 import/export actual0. 게임 코어03·아트·VFX·음향·드롭/성장 수치는01에서 유지하고 뷰 2파일만 바꿨다.
- `verification-view-02/REPORT.ko.md`: 실제 scene 인스턴스의 독립53검사 actual0·의도 실패54검사 actual1. 논리키/physical fallback·release/echo·중첩 모달·같은tick 패배HP0·재도전HP120·장착 무회복을 확인했다. 최초 fixture 종료 ObjectDB/1resource warning을 보존했고 verbose 재실행은 깨끗했다. 원인은 확정하지 않았으며 누수0을 주장하지 않는다.
- 새1920×1080 메뉴 smoke actual0, 다섯 역할의 가져온7상태·PNG raw fallback0을 확인했다. 후보02의 전체 GPU 실행은 반복하지 않았다. 후보01의1080p 자동 승리/p95를 후보02 정식 성능으로 바꾸지 않는다.
- `native-runtime-02/OBSERVATIONS.ko.md`: 부모/root가 일반 메뉴의 실제 Windows 창을 CUA로 직접 조작했다. 자동 pilot/시작/초점무시/입력observer 없이 명시 QA PNG만 사용했다. 1440×810에서 메뉴3개·성장 카드가 맞고, Esc로 choice→pause→같은choice, I 장비, 무기 피해14%/발사체+1·부적 회수+1m/주기8% 비교·장착을 확인했다. 장착은 현재HP를 회복하지 않았다.
- 월드 좌클릭 이동·카메라 이동, Space 뒤 회피 대기3.0초, M의 `소리 꺼짐` 안내를 확인했다. 실제 음향 청취는 아니다.
- 실제 rank1→4·선행 패시브·약29초 주력 화염 진화, 냉기/번개 습득과 냉기rank2·3기술 HUD를 확인했다. 실제57.433333초/499처치/레벨9/소유4개에서 패배했고 HUD0/120이 보였다. R+Esc로 새 판의clock0·처치0·레벨1·HP120/120을 확인했다. X 종료 actual0, 오류/경고/QA 이름충돌이 없다.
- native02 원본/사본44파일·36PNG·해시를 보존했다. 이 판의 벽시계447.8초는 관찰/정지를 포함하며5–8분 장 완주 시간이 아니다. 실제 OS 정예 승리·WASD 물리 hold·별도 OS 초점상실·실청취는 미검수다. 자동 승리와 직접 조작 패배를 서로 다른 증거로 유지한다.

## 실행본01과 직접 조작 중 발견

별도 실행본01은 `builds/chapter1/chapter1-c2-candidate-20261031-01/AshenCloister-Chapter1.exe`다. EXE 109674608bytes, SHA256 `fc9e41da23af5ae004204bb3fb12f63d9c7acfc34adbf9e43d00e71d11be027d`. source42개를 외부 staging으로 복사했고 PCK78개 checksum·동적 로딩 자원·제외 경로를 감사했다. import/export와 실제 EXE 자동 일반 입력 실행은 actual exit0이다.

실제 1920×1080 / Forward+ / RTX2070SUPER에서 78.15초 실제 정예 처치·813처치·3기술 시전/명중·화염 진화·장비9개 회수·4슬롯 장착을 기록했다. 다섯 역할의 방향/행동 상태를 읽었고 PNG raw fallback은0이다. p95는20ms/4522표본으로 목표16.67ms에 못 미쳤다. 동기 PNG·자동 입력이 있는 한 번의 실행이므로 정식 GPU/최종 성능 합격이 아니다.

부모가 실행본01의 1440×810 메뉴와 성장 선택을 직접 조작했고 화면은 들어맞았다. 정지한 채 싸운 시도는 약14초/44처치/레벨4/획득2개에서 패배했다. 이는 이동 없이 선 상태의 관찰이며 일반 난도/빌드 불가능의 증거가 아니다. 같은 tick 종료 시 생명력 HUD가 실제HP0을 즉시 표시하지 않는 결함을 확인했다.

도구로 주입한 Esc/I/R의 논리 keycode는 정상이지만 physical keycode는 Pause로 들어왔다. 기존 physical-only 단축키와의 호환성 문제이며 실제 물리 키보드의 고장이나 일반 사용자 단축키 불능을 입증한 것은 아니다. 후속02에서 논리키 우선 처리와 HUD 갱신을 수정했고 독립 fixture와 부모 실기로 확인했다. 실행본01과 실제 종료0, 재도전 후 같은 캡처 이름을 거부한 원시 로그도 남긴다. 실제 물리 키보드 hold와 별도 OS 초점상실은 아직 검수하지 않았다.

## 남은 품질과 제작 범위

1. C2는 품질 관문이 열려 있다. 반복 바닥·삼각 잔디·기하 기둥/소품, 군중 겹침과 주인공/위험 판독을 계속 개선한다.
2. 2.5D의 전용 idle과 남쪽 외 행동, 키프레임 사이 일관성·접지·읽히는 피격/처치, 연속 전투의 효과/카메라/소리를 검수한다. 실제 음향 청취를 수행했다고 주장하지 않는다.
3. 1080p 성능 목표, 직접 입력의 성장·장비·정지/초점·승패·재도전, 다른 시작 기술/선택 경로를 같은 후속 실행본에서 확인한다.
4. 1장 연결3구역·보상 이벤트·정예 변형·고유 보스/단계·보상 보존·저장/재도전과 5–8분 전체 흐름은 미완료다. 현재 약90초를 전체1장으로 축소하지 않는다.
5. 1장 품질을 통과하기 전 2·3장 콘텐츠를 확장하지 않는다. 검사 수·단일 자동 승리·이전 합성300적 측정으로 표현/재미 미달을 대체하지 않는다.

## 문서와 보존

v02 제작 도감은 `book-v02/dist/index.html`이다. v01의 14목차·39브리프를 복제한 뒤 현재C2·실행화면·실제아트 3목차를 추가했다. v01 도감50파일과 ZIP는 보존했다. 부모가 약1265×715 데스크톱 IAB에서 표지·현재C2·갤러리14장·실제아트·IT003 상세를 확인했다. 후보/코어 명칭·실제아이템 매핑·대체텍스트·캐시버전을 수정해 다시 확인했다. 새 모바일/전체 메모·인쇄 재검수는 하지 않았다. 루프백 임시 서버는 소유PID를 확인해 종료했다. 자세한 범위는 `docs/BOOK-VISUAL-QA.ko.md`다.

변경 전 인계/상태 원문은 `C:/Project/game-research/implementation-backups/chapter1-c2-docs-before-20261031-01/`에 보존했다. 최신 요약을 추가한 두 원본 문서는 이전 bytes를 exact suffix로 남기고 `FINAL-PRESERVATION.json`에 비교 결과를 연결한다. 기존 source51·phase7 EXE·사용자 equipment/progress 두 저장의 시작 핀을 유지한다. 미핀된 과거 증거 전체의 바이트 불변이나 과거 보고서 복구를 이번 선택 핀 검사로 입증하지 않는다.

커밋·외부 업로드·유료 자산 구매·원작 보호 자산 복사는 하지 않았다.

## 최종 문서 산출물

- [제작 도감 ZIP](C:/Project/d2r-combat-baseline/plans/chapter1-c2-20261031-01/CHAPTER1-PRODUCTION-BOOK-v02-20261031-01.zip): 50403805bytes, SHA256 `5545bca1be62d95ed61be9f657aead8c1d8af3892977ab298fe49678e412b20f`.
- [도감 산출물/해시](C:/Project/d2r-combat-baseline/plans/chapter1-c2-20261031-01/BOOK-ARTIFACTS.json): dist98파일·ZIP103항목, ZIP CRC 및 dist 전항목 SHA 불일치0. EXE를 ZIP에 중복 포함하지 않았다.
- [정적 도감 검사](C:/Project/d2r-combat-baseline/plans/chapter1-c2-20261031-01/docs/book-static-qa-final.json): 17목차·39브리프·25참고장면·14실행이미지·PNG12개, 정적115링크·참조/해시·JS구문·실제장비4개 runtimeID/이름 일치.
- [부모 데스크톱 도감 검수](C:/Project/d2r-combat-baseline/plans/chapter1-c2-20261031-01/docs/BOOK-VISUAL-QA.ko.md). 신규 모바일·전체 메모/인쇄 재검수는 제외했다.
- [최종 보존 비교](C:/Project/d2r-combat-baseline/plans/chapter1-c2-20261031-01/FINAL-PRESERVATION.json): actual0/success:true. 과거source51 현재/사본·phase7EXE·사용자저장2·v01도감50파일/ZIP·core03pin9 현재/사본·현재runtime42/staging·EXE의 선택 핀 불일치0. HANDOFF/IMPLEMENTATION-STATUS의 이전 원문은 exact suffix다. 미핀된 과거 증거 전체의 불변/복구를 주장하지 않는다.
- 루프백 임시 서버의 명령줄/PID를 검증한 뒤 소유PID27196만 종료했다. `docs/preview-8767-stop.json`의 stopped:true 및 명시적 stop에 따른 도구session actualexit1을 기록했다.

이 산출물 동결은 현재 플레이테스트 후보와 문서의 증거를 고정한 것이며 C2 최종 품질/1장 완성 승인으로 해석하지 않는다.
