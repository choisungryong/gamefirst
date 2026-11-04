# C2 패키지 후보01 · anti-pattern 검토

2026-10-31. 표현/패키징 소스와 실제 EXE 실행 증거를 새 검토자가 확인했다. 전체 제품 보안 감사나 SACRATA 품질 승인으로 해석하지 않는다.

| 방지 대상 | 현재 후보에서 확인한 결과 |
| --- | --- |
| 기술 검사 수·단일 자동 승리를 최종 품질로 대체 | RUN/closure/build/결과 scope가 대표 전투 후보임을 명시한다. 전체1장·품질 합격을 주장하지 않는다. 정상 코어 pilot 5/6 및 패배 실제exit1을 별도로 보존했다. |
| HP/XP/아이템/시간 승리 조작으로 정상 플레이 주장 | 뷰의 명시 QA driver는 이동·실제 제시 카드 선택·소유 장비 장착·dash만 요청한다. 코어를 직접 쓰는 경로가 없다. 정예 실제 사망이 승리 조건이다. |
| FX/애니메이션 callback이 피해 결정 | 없음. effects/actors는 사건과 상태를 소비하고 게임 수치를 쓰지 않는다. |
| 발사된 공격이 장착/성장 변경을 뒤늦게 읽음 | 뷰가 발사 context를 변경하지 않는다. immutable paid context의 수치 검증은 코어03 독립 검증으로 분리한다. |
| 무제한 파편·음향·배우·프레임 로그 | 표현 capacity와 15000개 frame 표본 상한이 존재한다. 실제 packaged pilot events overflow0, peak projectiles28이다. 최대 capacity 동시 부하 성능을 검증했다는 뜻은 아니다. |
| 에디터에서만 보이는 이미지/누락된 dynamic load | 실제 EXE READY에서 5역할×7상태를 확인했고 raw_texture_fallbacks는 빈 배열이다. PCK에 11 PNG import·10 WAV import·JSON6 등 런타임 closure가 포함된다. |
| 연구 원본·보호 자산·증거·테스트를 통째로 제품에 포함 | 외부 staging은 명시42개만 복사한다. PCK78 항목에서 forbidden 경로가 없고 현재 제품은 독립 생성 PNG/기존 독자 합성 WAV를 쓴다. 원작 로컬 D2R 파일 접근은 없다. |
| 기존 제품/사용자 save/역사 증거 덮기 | builder는 새 staging/output/proof 경로가 이미 있으면 중단한다. old source51·old EXE·현재 사용자 save2 hash 불일치0이다. 신규 JSON/PNG 증거만 작성했다. |
| 실패를 성공exit로 덮음 | import/export 실제exit0, package pilot 실제exit0을 각각 보존한다. 정상6사례 전체exit1을 숨기지 않는다. wrapper는 프로세스 returncode를 그대로 반환한다. |
| QA를 기본 조작으로 숨김 | pilot 및 focus 무시 옵션은 명시 플래그이고 READY/결과에 기록된다. 부모용 native menu에는 autostart/pilot/focus 무시를 넣지 않았다. |

확인한 제한: 선택적인 QA PNG 캡처는 한 폴더에 `frame-005.png` 같은 이름을 쓴다. 재도전으로 같은 시각을 다시 찍으면 덮지 않고 오류를 알린다. 이는 증거 보호를 위한 QA 출력 경계이며 전투 결과를 바꾸지 않는다. 여러 런을 캡처할 때는 새 실행/새 폴더를 사용해야 한다. 이번 단일 package pilot에는 충돌이 없다.

실제 UI 조작·정상 OS 종료·음소거의 소리 확인·재도전·성장/장비 모달 가독성은 부모 native QA가 별도 기록한다. 코드 체크리스트로 이를 대체하지 않았다.
