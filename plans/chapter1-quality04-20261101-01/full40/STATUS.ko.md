# 후보40 실행 패키지 통합 결과

2026-11-11. **UI40 + 냉기39 실행 패키지 통합 확인을 통과했다.** 최종 미술·재미·전체 수동 완주·성능·음향 청취 완료와는 구분한다.

## 제공 파일

`C:/Project/d2r-combat-baseline/builds/chapter1/chapter1-full-candidate-20261111-40/AshenCloister-Chapter1.exe`

- SHA256: `b7e1f7ec490b22bec9ec04a29827f6f9b6bd2e3cd296d65f28995fe3dea4abfb`
- 크기:134,245,608 bytes
- 명시적 런타임172개 / 스테이지174개 / PCK311항목
- 새 저장 공간: `AshenCloisterChapterOneQuality40`

변경된 기존 소스는 `chapter1/chapter_one_view.gd` 한 파일의 HUD/효과 preload 두 곳이다. UI40은 보관함 슬롯·등급·정렬, 실제3구역 진행띠, 결과 위계를 개선했다. FX39는 냉기 시전·비행·명중·빙결·파쇄 표현을 정돈한다. Core37/World37c/Actor36/Input21·데이터·음향·모델은 동일하다. 원화41과 별도 UI41 작업은 이 패키지에 포함하지 않는다.

## 실제 패키지 확인

고유40 스테이지에서 import/export 종료0. PCK의172개 의존·JSON/텍스트 해시·시험/연구/도구/초상41 불포함 감사를 통과했다.

실제40 EXE의 내장 PCK를 사용한 Vulkan Forward+ RTX2070SUPER 실행에서 **26개 확인 모두true, 종료0, stderr0**이었다. 새 HUD40/FX39 클래스, 실제3구역 패널, 30틱 시작 구간의 실제 냉기 이벤트 전달, 현재 프로필·보관함 읽기, 기존 장착 연속성, 키보드 시작, I 장비/ Esc 닫기·정지·복귀, 성장 Tab 포커스·선택1회·낡은 token 거부를 확인했다. UI40 필터/정렬과 지연 결과 포커스의 개별 검증은 앞선 UI40 증거를 따르며 전체를 다시 반복하지 않았다.

현재38에서 가져온40 프로필은 schema1/revision3/장비23개/완료한 도전1/갑옷storage_id1이다. 이 수치는 테스트가 지급한 값이 아니라 채택 시점의 현재38 진행이다. 프로필의 본문과 모든 revision journal을 바이트 그대로 최초 한 번 fork했고, 검사 중 장착·해체·저장 요청을 하지 않았다.

실제 화면5장: `native01/{menu,stash,combat,inventory,growth}-1280x720.png`. 담당자가 실제 combat/stash 캡처도 직접 확인했다. 이 짧은 입력 검사는 전체 수동 승리나60초 성능 측정이 아니다.

## 보존

원37/38 프로필 각각4개, 최초fork40 프로필4개가 검사 전후 바이트 동일하다. 원37/38 스테이지·freeze·EXE, 루트40과40 스테이지의 해시도 불변이다. `FINAL-PRESERVATION.json`에 결과를 기록했다. 미래 사용자 플레이로 revision이 변하면 그 진행을 보존하며 과거 값으로 되돌리지 않는다.

독립 사본과 원 조립본은 `ADOPTION.json`의 backup 아래 있다. [복귀 절차](ROLLBACK.ko.md)는 현재40 조립 파일이 이후 수정되지 않았을 때만 원38 조립으로 돌아가도록 한다.40 실행본·저장·원시는 삭제하지 않는다.

## 감사 도구의 첫 오탐과 복구

첫 export는 성공했지만 helper의 너무 넓은 `_probe` 금지 문자열이 정식 런타임 `chapter1/presentation/frame_probe.gd.remap/gdc`를 잘못 차단했다. `BUILD-AUDIT-ATTEMPT01.json`에 실패를 보존했다. 금지 조건을 실제 시험 helper 이름으로 좁힌 후 **동일한 EXE를 읽기 전용 audit로 다시 확인**했다. stage·export를 덮어쓰거나 재export하지 않았다. 이 오탐을 제품 파서/런타임 오류로 표시하지 않는다.

관리 툴과 합의한40 선택 관문은 `closure.json`, `build.json`, `pck-audit.json`, `PACKAGED-INTEGRATION.json`, `packaged-integration-execution.json`이다. 현재 모두 성공 조건을 만족한다.
