# 냉기39 표현 개선 검증 — 2026-11-11

후보38 제품은 보존하고 냉기39 신규 스크립트·셰이더5개를 독립 검증했다. root가 실제 원경·빙결 화면을 확인해 광량/별 모양 덩어리를 줄이고 적 실루엣을 덜 가리는 정돈 개선으로 승인했다. 최종 미술·SACRATA 수준 완성·전체 승리·성능 승인을 뜻하지 않는다. 별도39 제품 패키지는 만들지 않았다.

## 수정한 결함

새 `frost39_cast`를 부모가 알 수 없는 stroke로 받아 arc의 `from/to/width`를 읽는 충돌을 발견했다. 신규39 `sync`에서 release만 부모 처리 전 분리하고 실제 playing일 때 수명을 한 번 감산한 뒤 같은96개 stroke 풀에 되돌린다. 기존 코어·효과36·38 조립본은 수정하지 않았다. 상속된 파쇄 파편의 실제 수명은 .48초이며 잘못된 .42초 설명만 바로잡았다.

## 실제 Forward+ 비교

- stage: `C:/Project/game-research/build-staging/chapter1-frost39-preview-20261111-01`. 후보38 closure166개+새39파일5개, 준비 시61,671,287바이트. 거대한 루트 전체를 import하지 않았다.
- import·parser·helper parser 종료0. 실제 Forward+ 비교도 종료0, stderr 비어 있음.
- FX36/FX39에 동일 Core37·정상 QA 입력 정책·카메라를 사용해 각각3600틱을 진행했다. 실제 냉기 cast49/hit222/shatter2, 모든 step 코어 snapshot 해시 체인이 동일하다.
- 실제 이벤트 캡처는 cast tick1/hit tick18/shatter tick3577. 정지 동안 stroke/contact/fragment 수명은 두 변형 모두 불변이다.
-39 라우팅 최대치는 projectile7/contact9/impact2/cast1이었다. 이는 해당60초 표본 관측이며 전체 상한·성능 보장이 아니다.
- 자연 표본에서 살아남는 빙결은0프레임이었다. 이 결과를 빙결 형태 실검증으로 확대하지 않았다.

원시: `verify01/compare.log`, `compare-execution.json`, `captures/RESULT.json`, `captures/{36,39}-*.png`.

## 별도 빙결 fixture

최초 fixture는 rank1의 실제 `freeze_stacks=0` 때문에 실패했다. `verify01/frozen-fixture/RESULT.json`의 false와 로그를 보존했다.

수정 fixture는 정규 성장 XP12→제공된 서리창 rank2 카드 선택→원래 elite 정의 생성→현재 rank2 효과를 사용한 실제 코어 피해 함수4회를 적용한다. HP·`frozen_until`·제품 수치는 직접 주입하지 않는다. 정상 자동 시전 플레이를 대신하는 검사는 아니다.

두 변형 모두 HP165888, tick6/`frozen_until=12`, 결정4개, 코어 해시 동일. 정지8회 sync 동안 `ice_targets` 불변, 실제 tick30에는 결정0개로 만료했다. 종료0. 원시와 실제 화면은 `verify01/frozen-fixture02/`에 있다.

## 같은 사건의 확대 비교와 보존

`frost39_event_positions.gd`로 같은 코어/카메라를 headless 재생했다. 원래 두 실행과3600틱 코어 해시가 일치한다. 사건 위치를 카메라로 투영하고 논리1600×900→실제1280×720 배율.8을 적용해 원시 PNG의 같은240×180 영역을 그대로 잘랐다. 색·형태를 보정하지 않았다. 위치·범위는 `verify01/CROP-METADATA.json`, 결과는 `verify01/crops/compare-{cast,hit,shatter}.png`다.

후보38 root freeze168개·원래38 stage168개·38 EXE와 원37/38 프로필8개 핀 모두 해시 불일치0. 원시 `verify01/PRESERVATION.json`. 저장 복원·덮어쓰기·정규화는 하지 않았다. 모든 소유 Godot 프로세스는 종료했고 GPU를 반납했다.

다음은 UI40과 통합할 제품 후보에서 적용한다. 중간39 빌드나 추가 전체 검사를 반복하지 않는다.
