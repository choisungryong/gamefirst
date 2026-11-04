# 전체1장 후보11 · 표현 개선 · 목표 active

최신 실행: `builds/chapter1/chapter1-full-candidate-20261101-11/AshenCloister-Chapter1.exe`.
SHA256 `1f7f9cc16b53776a0dd65cb376c43016bc66789082c208435b938d91bb796fac`, 129170136bytes, runtime92/stage94/PCK164.
freeze SHA `b9ad5b165ae1565dd27a33969f1eba27e7ba1d7466da921eb5d17b4bf930862a`.

실제 영웅53골격/5클립, 거리 기반 보행/연속회전/상체 시전·피격, 독립 코드 지팡이를 연결했다. 로브의 무가중치 정점2053과4개 약한 가중치를 원본 보존 파생물에서 수정했다. 라이선스는 CC BY-SA3.0, 저자thecubber/원리그Julius·OGA. PCK와 별도credits에 출처가 있다. 새 `chapter1/art/QUALITY11-LEDGER.json`과credits사본을 따른다. 원작 보호 자산은 추가하지 않았다. CMU 모캡은 조사만 했고 사용하지 않았다.

둥근 식생720장을545군락/11,492곡선 풀잎으로 대체하고 바람/뿌리 명도/판석 조명 요철·MSAA4x를 연결했다. 실제 지형 충돌을 추가하지 않았다. 실제 hit에0.13초 흰 섬광(consume당8/전체96)을 추가했다. 시전은 하체10개를 보존하고 상체26개를 실제로 바꾼다. 앞 적만32%로 흐리게 하고 뒤/옆은100%, 원래 사체 페이드를 유지했다. 표현 fixture22/actual0/stderr0, 확대8m 이미지5장. 미술 완성 승인이 아니다.

전체 실제GPU 정상 입력은 **21749틱/362.4833초/3185처치/Lv11/주력진화/고유보상 소유**로 승리했다. 첫 승리 snapshot의 mode/tick/kills/hero/growth/metrics/chapter/equipped/inventory/elite_reward_uid가09와 모두 같다. 자동 정책은 이동/실제 선택/장착/회복약만 사용한다. 이후 root가 CUA로 승리·23개 보상·마지막 잿꽃의 유언(-10%피해/+1발사체/화염처치폭발)을 직접 선택/장착했다. 현재 장비 열 변경/적용 알림/완료 화면 복귀를 확인했고 최종raw weaponUID36·HP37703 유지와 일치한다. 전체 도전의 수동 플레이가 아니다.520초 wall 종료0/stderr0/23PNG. `GPU-FULL-RESULT.json`은 첫 자동 승리와 후속 UI 최종 상태를 분리한다. `NATIVE-REWARD-UI.json`. 저장은 명시적으로 껐으며 실제 보관함 저장 승인이 아니다.

후보10은 import/export0 이후 모델출처MD 누락으로 PCK 감사가 실제1 종료했다. 원 preset의 *.md 배제가 원인이었다. 실패10 EXE/stage/freeze/log는 그대로 남겼다.11은 격리 preset에서만MD 배제를 제거하고 명시 출처 파일의PCK 해시도 확인했다. 루트 Baseline main/export preset은 유지했다.09 source freeze85개 중 변경은 chapter_one_view.gd의 표현 preload3개뿐이며 이전 바이트는 full10-before 백업에 있다. 나머지09 runtime/core는 같다. 기존09 EXE와 baseline51/backup77/oldEXEs3·사용자저장2/oldstage72 선택핀을 확인했다. 역사적 모든sidecar 불변 주장은 하지 않는다. 리깅 폴더의 연구용.gdignore는 채택 후 정상 import를 위해 같은백업으로 단일파일 이동해 보존했다. root 전체 editor import는 하지 않았다.

`SACRATA-COMPARISON.ko.md`는 기존25개 유효 관찰과 추가 재생표본/우리09·11의차이를 제작 단위로 정리한다. 소리·원작 내부 규칙·전체 프레임을 확인한 것으로 쓰지 않는다. `rigged-hero-05/hero-comparison-24s.mp4`는09 대 연구05의 같은입력/같은전투상태·오프라인30FPS 영상이다. 후보11 최신 영상으로 바꿔 부르지 않는다.

도감 `book-v05/dist/index.html`:8페이지,110로컬참조 누락0,1440desktop/390mobile의8페이지 제목/이동/가로 넘침 확인. 비교/표지/모바일 검증 화면과24초 video metadata/재생을 관찰했다. 제목의 마지막 한음절 줄바꿈을 keep-all로 고쳤고 긴hash 모바일줄바꿈을 적용했다. initial BUILD/이전CSS/REVISION02를 보존했다. 인쇄/모든사진/모든터치상호작용 검수는 아니다. 임시탭/localhost8781 정리, 남은기존탭1(옛localhost8768)은 변경하지 않았다.

다음 최우선은 공통 스프라이트인 정예/보스의 고유 실루엣·리그/예고·공격·회복·사망과 냉기/번개의 큰 형태다. 이어서 큰 공간의 깊이/보상/장비 목록 선택 때 스크롤 초기화, 새 보관함 실제 비어 있지 않은 재시작·저장 경쟁 구간을 보완한다. 최종 아트의 수동5–8분/실청취/동일1080p3회 성능을 통과해야 한다. 기능 검사나 새 리깅 하나로 SACRATA 품질을 승인하지 않는다.2·3장으로 넘어가지 않으며 목표active를 유지한다.
