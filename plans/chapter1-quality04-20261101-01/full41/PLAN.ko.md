# 후보41 메뉴 원화 통합 패키지

2026-11-12. root의 UI41 코드·시각 승인과 분리 검증26개 통과 후 채택·최초 저장 복사·빌드·짧은 실제PCK 확인을 승인받았다. 이 문서는 계획이며 성공 증거는 별도 결과 파일이다.

## 범위

후보40의172개 명시적 런타임에 UI41 GD·마녀 초상PNG·AI 생성 출처MD 세 파일을 추가해175개로 고정한다. project/preset까지 스테이지177개다. 루트 조립 변경은 HUD40→UI41 preload 한 곳뿐이다. 냉기FX39·UI40·코어·데이터·음향·3D 모델은 그대로다. 초상은2D 타이틀 원화이며3D 외형 완성이 아니다.

빌드ID는 `chapter1-full-candidate-20261112-41`, 증거는 `full41`, 최종 시도 실행본은 `builds/chapter1/chapter1-full-candidate-20261112-41-attempt02/AshenCloister-Chapter1.exe`, 스테이지는 `C:/Project/game-research/build-staging/chapter1-full-candidate-20261112-41-attempt02`, 새 저장은 `%APPDATA%/AshenCloisterChapterOneQuality41`이다.

## 보존과 최초 복사

현재 루트40 freeze와 원37·38·40의 스테이지·실행본·manifest 해시를 확인한다. 각 사용자 저장 본문과 **현재 존재하는 모든 revision journal**을 읽기 전용으로 목록·해시·독립 사본에 보존한다. 과거 파일 수나 revision을 강요하지 않는다. 사용자 게임이 실행 중이면 종료하지 않고 중단한다.

41 저장·스테이지·출력·독립 백업은 처음에 없어야 한다. 존재하면 덮어쓰지 않는다. 현재40 저장 본문과 모든 journal을41에 최초 한 번 바이트 그대로 복사한다. 정규화·persist·보상 지급·초기화·기존 진행 복원은 하지 않는다. 이후40과41 진행은 독립이다.

최종 UI41 GD·원화PNG·출처MD를 포함한175개+project/preset을 동결한다. 출처MD는 분리 검증과 소비 용도를 설명하는 불변 기록이며 실제 제품 상태는 `STATUS.ko.md`로 따로 기록한다. 이후 성능 바인딩 종료까지 런타임/출처 바이트를 변경하지 않는다.

## 패키지와 확인

고유41 스테이지에서만 import/export한다. 기존40 export의 명시적 목록에 세 파일만 추가한다. PCK 의존175개·JSON/텍스트 원본해시·시험/연구/도구 불포함을 감사하고 기존40 credits에 AI 초상 출처를 추가한다. 실패 원시와 이미 생성한 디렉터리는 덮어쓰거나 삭제하지 않는다.

새 EXE의 실제PCK Forward+에서 메뉴 원화 로드·포커스/Tab·보관함 읽기와 복귀·실제 세 시작 기술ID·짧은 냉기 이벤트/경로 연결·프로필 바이트 불변을 확인한다. 이미40에서 통과한 성장·장비·정지의26개 전체를 반복하지 않는다. 이 확인은 전체 수동 완주나 성능 승인이 아니다.

모든 원37/38/40 저장·실행본·스테이지, 최초fork41 저장, 새 루트/스테이지41을 전후 비교한다. 사용자 정상 진행이 감지되면 멈추며 과거값으로 되돌리지 않는다.

계약은 `closure.json`(175/177), `build.json`(EXE bytes/SHA), `pck-audit.json`(success), `PACKAGED-INTEGRATION.json`(success), `packaged-integration-execution.json`(종료0·timeoutfalse·launch_error null), `FINAL-PRESERVATION.json`(success/preserved_previous_builds/profiles_byte_identical/source41_and_stage41_unchanged)이다.

## 최초 감사 실패와 보존된 재시도

최초41 import/export는 종료0이었으나 새 비리소스 출처MD가 기존 preset의 `include_filter`에 없어 PCK 감사에서 실패했다. `export_files`에 명시하는 것만으로 MD가 포함되지 않았다. 이 실패를 성공으로 바꾸지 않는다.

원래41 스테이지와 EXE는 원위치에 보존했다. 최초 closure/staging/import/export 실행 기록과 감사 실패는 절대 경계를 확인한 `Move-Item`으로 `full41/attempt01`에 되돌릴 수 있게 옮겼다. `ATTEMPT01-PRESERVED.json`은 그 파일들과 원래 스테이지·EXE의 해시를 계속 검사한다. 루트 소스 freeze와 최초41 저장 복사는 변경하지 않았다.

root 승인 후 고유 `-attempt02` 스테이지·출력에서 같은175개 소스를 사용하고 정확한 출처MD 한 경로만 `include_filter`에 추가한다. 기존 EXE·스테이지·원시는 덮어쓰지 않는다. 최종 공식 manifest는 실제 attempt02 경로를 새로 기록하며, 성공 여부는 여전히 감사·실PCK·최종 보존 결과로 판단한다.
