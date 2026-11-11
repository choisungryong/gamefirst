# UI38 구현·실제 화면 결과

## 최신 상태 — 후보38 실행 패키지 준비 완료

root의 명시적 adoption/GPU GO 후 UI38을 채택하고 별도 후보38을 빌드했다. 실행 파일은 builds/chapter1/chapter1-full-candidate-20261107-38/AshenCloister-Chapter1.exe (134,224,600bytes, SHA256 `71daa23b7337598f65d1ab519bfb0f66fda0357941c40a8537aa8fae5e6c77e5`). 전체166runtime/168stage closure와303 PCK 항목을 추적했다. root 기존 파일 변경은 chapter_one_view.gd의 HUD preload 한 줄이다. 코어·데이터·월드·actor·FX는 동일하다. 새 UI3파일은 freeze와 ADOPTION에 별도로 기록했다.

원본백업 C:/Project/game-research/implementation-backups/chapter1-before38-20261107-01 에 root 원본3파일·UI3파일·전체 rootclosure 해시·원37freeze 사본·현재37프로필4개 읽기전용 snapshot을 보존했다. 원37stage165파일/EXE/freeze/현재 프로필4개 해시를 채택·빌드·검증 전후 비교해 모두 일치했다. 기존37 EXE/stage/userdata를 덮어쓰지 않았다.

원37의 현재 진행( revision3 / 장비23 / 완료1 / body1 )을 **처음 없던** AshenCloisterChapterOneQuality38 userdata로4JSON 파일 모두 byte-identical fork했다. normalize/_persist/보상지급으로 복사하지 않았다. 이후37/38은 별개 저장이다. 검증에서는38도 읽기만 했고4파일 모두 전후 해시가 같다.

검증: import/export0,166deps PCK audit 통과, 연구/계획/helper 미포함,15simsec profile-off headless 정책 smoke0. 실제 후보38 EXE의 embedded PCK를 사용하는 Forward+ 네이티브 검증22항목 모두 true·종료0: 독립38 저장경로/프로필 정상로드, 보관함 읽기·키보드복귀, Enter시작, 시작장비 연속성, I/Esc장비열고닫기, Esc일시정지/복귀, 성장모달Tab/한번선택/만료token거부, 프로필바이트보존,5화면캡처. 메뉴와 전투 캡처를 실제로 열어 확인했다. user profile을 쓰는 신호는 호출하지 않았다. 최종 성능/전체 수동 완주/청취 승인으로 주장하지 않는다.

근거는 package38/{ADOPTION,SOURCE-BEFORE,FINAL-SOURCE-FREEZE,USER-FORK,closure,staging-manifest,build,pck-audit,PACKAGED-INTEGRATION,FINAL-PRESERVATION}.json과 실행 raw stdout/stderr가 담긴 *-execution.json이다. 실제 패키지 캡처는 package38/native01에 있다. helper는 package38.py 및 packaged38_integration.gd이며 제품 PCK에는 넣지 않았다. GPU 슬롯을 반납했고 남은 Godot/Ashen 프로세스 없음. 아래는 채택 전 제작/검증 이력이다.

## 배경 대비 보정 (최신)

before-contrast01에 기존 HUD38을 보존했다. 같은 HUD38 파일에만 목표/생명·XP/회피·회복약의 절제된88%암색 받침과 상아색 텍스트를 추가했다. 목표 받침은460logical 너비로 제한했고 상단 동작 버튼은 작은 높이를 유지한다. 장식용 받침은 MOUSE_FILTER_IGNORE다. 임시 안내 Label도 공식 Label.normal StyleBox 배경을 사용한다. 패딩으로 생긴 discovery 겹침을 발견해, discovery가 실제 표시되는 동안 안내를 해당 카드의 아래로 배치했다. 기존 보스바 위치 규칙도 상속 유지한다.

world03과 world04는 동일 actualworld helper로720/1080 각각4화면을 렌더링했다. 둘 다 종료0, Vulkan Forward+, script/runtime오류 없음. world03은 최초 대비 보정 증거, world04는 discovery 아래 배치까지 반영한 최신8캡처다. 실제 combat720/1080을 열어 배경 위 텍스트 가독성과 discovery 간격을 확인했다. 로그/이미지 이전 폴더는 보존했다. GPU 슬롯 반납 및 잔여 Godot 없음 확인.37 assembly/저장/EXE 변경 없음. 전체 입력 회귀나 전체 플레이 검증을 반복한 것은 아니다.

## 집중 시각 수정과 실제3D 비교 (후속)

probe02 시점 소스는 before-refine01에 보존했다. 이후 성장 선택은1260×500logical 중앙 모달로 압축하고,70px 속성 인장과 자연 높이 내용으로 큰 빈 영역을 줄였다. 세 기술은 하단 중앙의 작고 실제 상태를 읽는 석재 슬롯으로 묶었다. 상단 동작 버튼은36px/15pt로 줄였다. 생명은 단순 링 대신 실제HP비율에 맞춰 수직으로 비워지는 붉은 원형 저장조로 바꿨다. 장비 화면은1360×600으로 압축하고 현재 슬롯이 빈 경우 한 줄만 표시한다. 현재 장비가 있을 때만 실제 차이 열을 추가해 후보 능력을 중복하지 않는다.

실제 ChapterOne stage를 로드하는 ui38_world_preview.gd를 추가했다. 저장 비활성 인자가 없으면 거부한다. 실제 코어240틱 뒤 멈춘 장면,64%HP 표시용 fixture, 실제 생성 장비 fixture로 전투/성장/빈 슬롯/장착 비교를720/1080 각각 캡처한다. 프로필 객체를 구성하지 않으며 보상·완주 증거가 아니다.

world01은 장비 제목 문자열의 타입 추론 오류가 발생한 실패다. 로그를 보존하고 소유한 고유38stage 프로세스만 종료했다. String 명시와 helper 직접 HUD preload로 수정했다. 새 world02는 종료0, script/runtime오류 없이8개 실제3D 캡처를 완료했다. 실제 렌더러는 제품과 같은 Vulkan1.4.341 Forward+ / RTX2070SUPER (world02.log). root가8개 캡처를 검토할 수 있다. 이 후속 실행은 gl_compatibility가 아니다. GPU 슬롯은 반납했고 잔여 Godot 프로세스가 없음을 확인했다.

후속 명령은 다음과 같다. world02 증거를 덮어쓰지 말 것.

```powershell
& 'C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe' --path 'C:/Project/game-research/build-staging/chapter1-ui38-preview-20261107-01' --rendering-method forward_plus --position 20,20 --quit-after 600 --script res://ui38_world_preview.gd -- --chapter1-profile-off --chapter1-qa-ignore-focus --ui38-output=C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/ui38/world03
```

실제 배경 위에서 생명/회피/목표의 별도 받침 없는 텍스트 대비는 후속 검토 여지가 있다. 아래 probe02 내용은 이전 UI 단독 검사 이력이며 후속 레이아웃에14개 입력 검사를 재실행했다는 뜻이 아니다.

새 제품 소스는 chapter1/view/ui38/chapter_hud_quality38.gd, life_seal.gd, element_seal.gd 세 파일이다. HUD36 상속을 유지한다. 붉은 생명 인장, 실제 생명·레벨·경험치, 세 기술, 회피·회복약, 목표를 재배치했다. 성장 카드는 큰 속성 인장과 속성별 상단 경계를 사용한다. 장비 비교는 두 석재 표면과 실제 후보/현재 stats 차이를 표시하며 긴 상세는 스크롤한다. 차이는 표시 전용이고 피해·장착·보상을 계산하거나 지급하지 않는다.

helper 소스: DESIGN.ko.md, ui38_probe.gd, 이 STATUS.ko.md. 실제 증거: import01.log, probe01.log/probe01, probe02.log/probe02. 첫 시도와 그 캡처는 보존했다. 외부 화면·기존 사용자 앱을 자동 조작하지 않았다. 프로필 구성 객체를 만들지 않는 UI-only real37 core fixture다. 전투 중앙이 빈 배경인 것은 이 UI 단독 fixture의 의도이며 전체게임 화면으로 주장하지 않는다.

독립 stage: C:/Project/game-research/build-staging/chapter1-ui38-preview-20261107-01. 기존37 stage의 runtime_source_files163개+project.godot/export_presets.cfg를 복사하고 새UI3개와 probe만 추가했다. stage-only chapter_one_view.gd HUD preload를 UI38로 변경했다. stage project 이름과 custom_user_dir_name은 UI38Preview20261107 고유 이름으로 변경해 엔진 로그도37 namespace에 쓰지 않는다. root assembly,37 stage/EXE, 사용자 프로필은 변경하지 않았다.

root exclusive GO 후 import01 성공, script/parse/runtime errors 없음. 첫 probe01은14checks 모두 통과했다. 직접 캡처를 확인한 뒤 고정24px였던 기존 emblem 대신 큰 native element_seal을 만들고 실제 장비 차이/상세 스크롤을 추가했다. 그 변경에 대한 probe02도14checks 모두 통과했고720/1080 각각 menu/combat/growth/equipment 총8캡처를 만들었다. 확인 항목은 modal 첫 포커스, Enter 시작, HP 실제 코어 일치, Tab 이동, 성장 선택 정확히1회, inventory scrollbar 유지, inventory close다. 최신 probe 소스는 결과 하나라도 false면 exit1이다. 이 failclosed 반환 수정은 probe02 완료 직후 적용했고 렌더링에는 영향이 없다.

보존된 probe02는 UI-only이며 전체게임 boss/discovery/save 실제 이벤트를 발생시키지 않았다. 해당 연결은 HUD36 상속을 유지했다는 소스 근거만 있다. 원래 세이브 회귀/플레이/전체 성능/오디오 완료로 표시하지 않는다. focus복원은 유효한 이전Control이 있을 때만 수행한다. 게임패드 지원을 추가했다고 표시하지 않는다.

실행 명령 (새 증거 디렉터리를 지정할 것):

```powershell
& 'C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe' --headless --path 'C:/Project/game-research/build-staging/chapter1-ui38-preview-20261107-01' --editor --import --quit
& 'C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe' --path 'C:/Project/game-research/build-staging/chapter1-ui38-preview-20261107-01' --rendering-method gl_compatibility --position 20,20 --script res://ui38_probe.gd -- --chapter1-profile-off --ui38-output=C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/ui38/probe03
```

GPU 실행 슬롯을 root에 반납했다. 제품 통합과 후보38 패키징은 root가 별도 조정한다. 커밋/푸시 없음.
