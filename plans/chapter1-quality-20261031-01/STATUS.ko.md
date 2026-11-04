# 품질03 진행 보고

2026-11-01, Asia/Seoul. 사용자 품질 미달 지적에 따라 대표 C2의 환경·동작·효과·HUD·음향을 개선했다. **SACRATA 목표 품질 통과와5–8분짜리1장 전체 완성은 아니다.** 기존 코어 규칙을 유지한 비교·플레이테스트 후보03이다.

새 실행: [AshenCloister-Chapter1.exe](../../builds/chapter1/chapter1-c2-candidate-20261101-03/AshenCloister-Chapter1.exe). 조작은 같은 폴더 [RUN.ko.md](../../builds/chapter1/chapter1-c2-candidate-20261101-03/RUN.ko.md).116516096bytes, SHA256 `c916e280facbc89c6fcb1b21ee9a3fc9725313e248956e1918342ac2d4602fbb`.

## 바뀐 결과

- 원형 음영이 큰 지면·삼각형 풀·상자 기둥을 판석/흙과 폐허12종·식생8군락으로 교체했다. 중앙 마당 반폭6.5×8m, 낮은 식생620개, 전체673소품과 접지 그림자, 아틀라스2표면이다. 높은 소품의 발은 플레이±19m 밖이다. 충돌 판정은 추가하지 않았다.
- 영웅4방향 각각4시전포즈를 연결했다. 이동 중 짧은 발사 포즈와 방향 유지, cosmetic 피격 반동/flash, 크기를 줄이지 않는 사망 fade를 적용했다. 생성한32포즈 달리기 두 시도는 실제 발 교대가 불충분해 거절했고 기존4프레임 보행을 유지했다.
- 백열 중심 화염/짧은 plume, 냉기 창/파쇄, 번개 리본/가지와 적의 낮은 알파 전조를 연결했다. 통합 화면의 불꽃 사각 경계를 수정했다. 카메라 반응은 제한되며 화면 흔들림을 끌 수 있다.
- 세 원소 HUD를 붙이고 Label 폭1px 때문에20–22줄로 잘리던 문제를 최소140px/두 줄 배치로 고쳤다. 가까운8m 안에서 드롭 이름을 보이고 품질별 색을 구별한다.
- 공식 Kenney CC0 자료를 레이어한20WAV/13voice를 새로 사용한다. 음원별 장부·공식 출처·라이선스3개를 제공한다. 실제 청취 승인은 아니다. 음소거 해제/master 변경 때 활성 cue의 개별 gain이 사라지는 P3는 [코드 검토](CODE-REVIEW.ko.md)에 기록했다.

채택 아트의 원본·프롬프트·해시는 [ASSET-LEDGER-v04.json](../../chapter1/art/quality03/ASSET-LEDGER-v04.json), 음원 처리·레이어·해시는 [AUDIO-LEDGER.json](../../chapter1/art/quality03_audio/AUDIO-LEDGER.json)에 있다. 기존 장부/원본/거절 시도는 보존했다. 보호되는 원작 자산은 새 패키지에 복사하지 않았다.

## 확인한 근거

독립 headless는 [158검사 actual0/의도159 actual1](verification-02/REPORT.ko.md), stderr 없음이다. 실제 씬의 동일tick HP0·재도전HP120·중첩 모달·논리키/physical fallback·장착무회복·표현 뒤 코어 불변·효과/음향 상한·4방향 시전·1280/1440/1920의3진화명 전체 표시를 확인했다. 합성 HP/성장 지정 경계 검사를 일반 플레이로 표시하지 않는다.

[통합 GPU preview03](world/REPORT-v02.ko.md)은 실제1920×1080/Forward+/45초 actual0, 셰이더 오류/종료 경고 없음, world/actor/audio rawfallback[]다. root는 동일19초/92처치 전후 표본과41초3기술 화면을 보고 환경 개선 및 HUD/불꽃 경계 수정을 확인했다. 비교 후보로 수용했으며 최종 목표 품질 승인으로 보지 않는다.45초 상태는 Lv10/324처치/화염진화4·냉기2·번개2다.

[패키지 감사](package03/build/build.json)는 runtime70/stage72/PCK122, payload checksum·명시적 동적 리소스 closure·금지 경로 부재·동일EXE headless fallback0을 확인했다. 기존 후보02/phase7 EXE2, baseline51/코어03의9pin, 사용자 equipment/progress2, 후보02stage44의 선택 핀은 유지했다.

[root 직접 조작 관찰](native-runtime-03/native-20261101-01/OBSERVATIONS.ko.md)은1440×810 메뉴/성장/정지복원·Space 회피대기·장비 비교/장착무회복·Mtoast·실제17.85초/80처치/Lv5/HP0/154 패배·R초기화120/120·창X 종료actual0/stderr0bytes다.20PNG와 실행/해시 원시를 보존했다. 수동 진화·세기술·정예 승리·OS WASD hold·긴좌클릭 이동·실청취는 확정하지 않았다. 관찰용으로 주로 정지한 수동 실행의 조기 패배를 승률이나 난이도로 일반화하지 않는다. 영웅 주변 적 겹침과 잦은 초반 성장 화면의 흐름은 개선 대상으로 남았다. 자동 모드 PNG가 모든 장착 직후를 찍지는 않으며 일부 즉시 변화는 root의 당시 CUA 관찰에 근거한다.

[품질03 전체90초](book-v03/dist/movies/new-720p30-offline.mp4)와 [이전 후보02 전체90초](book-v03/dist/movies/old-720p30-offline.mp4)는720p/고정30FPS 오프라인 렌더다. 두 후보의 기존 정상 입력/선택/장착 드라이버는78.15초/813처치/Lv12/화염진화4·냉기3·번개3/HP7210raw로 같은 승리 결과를 냈다. [같은20–60초 전후 비교40초](book-v03/dist/movies/candidate02-vs03-20s-60s-offline.mp4)는2560×768로 나란히 배치하고 소리는 후보03만 사용했다고 영상 상단에 표시한다. MP4는 도감 내부에 동일 해시 사본으로 보존하며 원시 AVI/명령/로그/ffprobe는 package03/movies에 남는다. 새 영상의2700frame 강제 종료 ObjectDB/9resource 경고와 이전 영상의 앱90초 정상 종료+3000frame guard/경고 없음은 구분한다. **고정 FPS 영상은 수동 플레이·실제 GPU 성능·실청취·누수0 증거가 아니다.**

[성능 진단02](performance-diagnostic-02/README.ko.md)는 동일EXE/실제1920×1080/Forward+/VSync해제·delta smoothing해제·max-fps120/normal pilot70초를 기록했다. actual0/stderr0,elapsed70/8344표본(<15000)/engine delta p958.333ms/698처치/Lv12/maxalive59/peakprojectile28이다. root의 실제 초점 확인은32초 한 시점이며 전체 프레임 초점 기록은 아니다.120FPS pacing과 엔진 delta, 단일 실행, 첫10초 미제외·60초×3 미수행·최대180적 부하 미검증이므로 정식 성능 통과가 아니다. 진단01은 uncapped로15000표본 상한을 채워 초반 일부만 기록했으므로 p951.389ms를 전체70초의 결과나 개선율로 쓰지 않는다. 원시를 보존했다.

## 도감과 보존

새 [품질 보완 도감 v03](book-v03/dist/index.html)은 전후 비교·환경·동작·효과/HUD·음향·장비·검증/영상·잔여 관문의8페이지다.5PNG/3JSON 카드와20WAV 재생 버튼, 실제 장비4종/효과를 담는다. 기존39상세 브리프와 관찰을 담은 [도감 v02](../chapter1-c2-20261031-01/book-v02/dist/index.html) 전체를 대체하지 않고 보존된 이력으로 연결한다. 정적 검사8HTML/로컬 참조 누락0/20audio/복사 해시 일치, 로컬HTTP69리소스200/동일크기를 확인했다. [root 브라우저 확인](book-v03/BROWSER-QA.ko.md)은1440×900표지·slider키50→51/8페이지제목·환경/동작/효과 이미지·실제 장비 표·비교 영상 일부 재생(20.194→37.223초)/첫 fire 재생 요청을 포함한다. 좁은443×882는 표지만 확인했다. 두90초 player·모든20음향·전체모바일·인쇄·실청취 승인은 아니다. 소유 IAB 탭을 닫고 viewport를 복원했으며 임시 루프백 서버를 중지했다.

HANDOFF 수정 전 바이트와 v02의104파일 해시는 `C:/Project/game-research/implementation-backups/chapter1-quality03-docs-before-20261101-01/manifest.json`에 보존했다. 갱신 HANDOFF의 exact suffix와 v02 불일치0을 확인했다. [DOCS-PRESERVATION-01.json](DOCS-PRESERVATION-01.json)을 따른다. 선택 핀 일치가 핀하지 않은 과거 증거 전체 불변이나 역사적 보조보고서2개의 복구 미입증을 해결했다는 뜻은 아니다. 커밋·업로드·유료구매는 하지 않았다.

## 다음 품질 관문

적이 영웅 주변에 겹쳐 쌓이는 가독성, 낮은 프레임의 동작·전환, 반복되는 둥근 식생과 평평한 음영, 연속 타격 타이밍·실제 전투 믹스를 개선해야 한다. 정식 전경1080p/비movie/PNG 없는 준비10초+60초 반복 성능도 열려 있다. 짧은 QA p95약20ms나 movie30FPS를 목표16.67ms 통과로 표시하지 않는다.

5–8분 전체1장의 연결3구역·이벤트·정예 변형·고유 보스/단계·보상 보존/저장은 아직 없다. 대표90초를 전체1장으로 축소하거나, 이 품질로2·3장을 먼저 확장하지 않는다.

