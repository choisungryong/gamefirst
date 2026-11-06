# 수동 장착·재실행 독립 검토 · 2026-11-06

읽기 전용 대조 후 별도 보존 사본만 추가했다. 게임/GPU/UI를 실행하지 않았고 제품 소스·실행본·사용자 프로필은 수정하지 않았다.

## 보존 대조

- `FINAL-SOURCE-FREEZE.json`의 루트 제품 파일 158개를 SHA256으로 전수 대조: 누락·불일치 0.
- 후보36 `AshenCloister-Chapter1.exe` SHA256: `a889be6fcb57120083d78e84dacd4ae4976482edb04285ef017dbf37e993e22f`, build 기록과 일치.
- `USER-PRESERVATION-ADDENDUM02.json`의 현재 사용자 파일 9개 전부 SHA256 일치. 기존23·29 및 원36 revision1 journal 불변.
- `manual-loadout01`의 변경 전 보존 파일 8개를 각각 원핀과 대조: 전부 일치.
- 변경 전36 프로필과 현재36 프로필을 JSON 파싱 후 각 최상위 필드 전체 직렬화 비교: `equipped`와 `revision`만 다름. `equipped`는 `{}`→`{"body":1}`, revision은1→2. 아이템22개·완료1 및 나머지 전체 필드 내용 동일.
- `post-selection-preserved`에 현재 핀9개와 ADDENDUM02를 추가 복사했다. 복사 파일 SHA256을 원핀·원파일과 다시 대조했다. `post-selection-preserved/MANIFEST.json`에 원경로·보존경로·바이트수·해시 기록. 이전8개 사본을 덮어쓰지 않았다.

## 능력치와 UI 관찰의 범위

기본HP120×256 + 선택한 storage_id1 흉의의 `max_hp_raw`12517 =43237raw, 실제HP168.89453125. `cloister_hud.gd:174`는 ceil을 사용하므로169표시가 일치한다. `chapter_hud.gd:37`의 장비 옵션은 정수 표시라 +48이며, 게임 수치 불일치의 증거가 아니다. 기본 능력치 합산은 `combat_run.gd:219`를 따른다.

`RESULT.json`은 두 독립 UI 실행의169HP, 현재 장착 패널, 이동·회피·정지를 기록한다. 원 채팅의 실제 Computer Use 출력에는 관련 스크린샷이 있으나 이 폴더에는 별도 PNG나 launch/PID/exit/stderr 원시가 없다. 따라서 이 검토는 해당 UI 관찰을 새로 독립 재현한 검사가 아니다. 파일 상태와 수치 정합성만 독립 대조했다. 기존 결과가 명시한 전체 수동 승리·실청취·focused성능·종료 경고 해결 미승인은 타당하다.

## 후속 작업

전체 수동 검증은 보존된 현재 장착으로 새 도전의 시작→성장선택→장비비교→문 통과→보스·보상까지 이어지는 한 판이 남아 있다. 정지·재개·회복약·장비 메뉴를 최소 입력으로 점검하고, 수동 UI 증거는 고유 폴더에 남긴다. 실청취는 실제 오디오 입력을 받을 수 있는 경로가 확인된 경우에만 승인한다.

번개 진화 이름의 정확한 위치는 `chapter1/data/growth_quality36.json`의 `chapter1.skill.arc.evolution_name`, 현재 `두 갈래 폭풍`이다. 같은 정의의 랭크 갈래수는1·1·2·3, 진화는3이다. `combat_run_stun36.gd:86`이36카탈로그를 로드한다. 기존 `root-resume-01/balance36_rules.gd:42`/`balance36/rules02/RESULT.json`은 랭크3의2갈래·랭크4의3갈래·진화연쇄대상8을 확인했으나 진화갈래3 자체와 이름 정합성을 직접 검사하지는 않았다. 기존 기본 `test_growth.gd:80`의2갈래 검사는 역사적 기본카탈로그용이므로 바꾸지 않는다.

제안하는 후속 최소 변경은36을 보존하고 successor 카탈로그37(또는 다음 비충돌 번호)의 진화명만 `세 갈래 폭풍`으로 바꾸는 것이다. successor 전투 loader도 새 카탈로그를 참조해야 한다. 새 정의의 파싱·기존 validator 확인과 전체 dictionary diff가 해당 문구1개뿐인지 대조한다. 실제 HUD 표시도 새 후보에서 확인하며36 freeze를 덮어쓰지 않는다. 이 검토에서 문구·loader는 아직 수정하지 않았다.
