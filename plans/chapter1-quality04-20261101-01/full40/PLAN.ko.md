# 후보40 통합 패키지 준비

2026-11-11. 이 계획과 도구 작성 단계에서는 조립본·사용자 저장·기존 스테이지를 변경하지 않고 엔진도 실행하지 않는다. UI40의 코드 검토와 포커스 수정 검증 후 root의 채택 GO를 기다린다.

## 조합과 경로

- UI40 보관함·3구역 진행·결과 화면 + 냉기39 표현을 한 실행본으로 통합한다. 중간39 실행본은 만들지 않는다.
- 기존38의166개 명시적 런타임 파일에39의GD1개·shader4개, UI40의GD1개를 더해172개다. 새 project/preset까지 스테이지174개다.
- 빌드ID: `chapter1-full-candidate-20261111-40`.
- 증거: `plans/chapter1-quality04-20261101-01/full40`.
- 스테이지: `C:/Project/game-research/build-staging/chapter1-full-candidate-20261111-40`.
- 실행본: `builds/chapter1/chapter1-full-candidate-20261111-40/AshenCloister-Chapter1.exe`.
- 새 저장 공간: `%APPDATA%/AshenCloisterChapterOneQuality40`.
- 독립 보존 사본: `C:/Project/game-research/implementation-backups/chapter1-before40-20261111-01`.

초상41은 원화 계획 자산이므로 후보40 런타임에 포함하지 않는다. 코어·데이터·오디오·모델도 변경하지 않는다.

## 채택 전 보존

기존38의168개 루트 freeze와 원38·37 스테이지, 각 실행본 SHA256을 확인한다. 현재37·38의 프로필 본문과 **현재 존재하는 모든 revision journal**을 읽기 전용으로 목록·해시·독립 사본에 보존한다. 과거4개 고정 목록이나 과거 revision으로 되돌리지 않는다. 사용자 실행 중이면 종료시키지 않고 중단한다.

40 저장 폴더·40 스테이지·출력·백업은 처음에 없어야 한다. 기존40 폴더가 있으면 덮어쓰지 않고 중단한다. 현재38의 본문과 모든 journal을40에 최초 한 번 바이트 그대로 복사한다. schema 정규화·persist 호출·보상 지급·초기화는 하지 않는다. 이후38/40의 진행은 독립이다.

루트는 `chapter_one_view.gd`의 HUD38→HUD40, FX36→FX39 preload 두 곳만 변경한다. 원본과 전체172개+project/preset의 전후 해시를 보존하며, 다른 기존38 파일은 불변이어야 한다.

## 패키징과 필요한 통합 확인

고유40 스테이지에172개 파일만 복사하고 기존38의 감사된 명시적 export 목록에 새6개만 추가한다. import/export는40에서만 수행한다. PCK의 모든 명시적 의존, 원본 JSON·출처 텍스트 해시, 연구/시험/도구/초상41 불포함을 검사한다. 이미 같은 기존 에셋에 해당하는38 크레딧을 복사한다.

새 실행 파일의 실제 PCK에서 짧은 Forward+ 통합을 한 번 확인한다. 별도40 저장 경로·실제HUD40/FX39 클래스, 현재38에서 가져온 보관함/장착 연속성, 키보드 시작·장비/I·Esc 정지/복귀·성장 단일 선택·낡은 token 거부, 실제 냉기 이벤트의 FX39 전달을 확인한다. 30틱의 시작 구간 외 전체 수동 완주/성능/음향 검사는 이 도구에서 반복하지 않는다.

검증 후 원37/38 본문·journal, 최초fork40 본문·journal, 원37/38 스테이지·실행본·freeze, 루트40·스테이지40 해시를 다시 확인한다. 정상 사용자 진행이 감지되면 실패로 멈추며 어떤 파일도 과거 값으로 복구하지 않는다. 실패 원시와 이미 생성한40 폴더를 덮어쓰거나 삭제하지 않는다.

## 실행 순서와 관리 툴 계약

`package40.py prepare`는 소스 경로와 개수만 출력하며 변이를 하지 않는다. `adopt`, `build`, `verify`는 각 단계별 root GO 이후 순서대로 실행한다. 한 번 생성한 증거 파일은 exclusive write로 다시 쓰지 않는다.

감사 도구 조건을 바로잡아야 하는 경우 `audit`는 이미 성공한 export의 같은 EXE를 읽기 전용으로 검증한다. 원 export 실행 종료0·원 경로·소스/스테이지/기존 후보 해시를 확인하며 재export나 덮어쓰기를 하지 않는다. 첫 감사 실패도 별도 증거로 보존한다.

관리 툴과 합의한 선택 관문은 이 폴더의 `closure.json`, `build.json`, `pck-audit.json`, `PACKAGED-INTEGRATION.json`, `packaged-integration-execution.json`이다. 172개 고유 의존과 필수6개, 감사/통합 성공, 실행 종료0·시간초과없음·launch_error null, 실제 EXE 크기/SHA 일치 후에만40을 선택한다. 그 전에는38 기준선을 유지한다.
