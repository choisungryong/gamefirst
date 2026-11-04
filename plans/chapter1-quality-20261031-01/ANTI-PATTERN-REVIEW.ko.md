# 후보03 금지 패턴 검토

2026-11-01, Asia/Seoul. `rg -n`으로 chapter_view, cloister_effects, cloister_actors, combat_audio의 FileAccess/DirAccess/OS, MAX, new, queue_free, seq, volume, sync 및 run 필드 대입을 검색하고 해당 함수·셰이더·패키지 closure를 읽었다. 제품 수정·GPU 실행은 하지 않았다.

| 경계 | 관찰 |
|---|---|
| 표현 계층이 전투 수치를 소유 | actor/FX/HUD에서 HP·XP·피해·스폰에 쓰는 경로를 찾지 못했다. 독립 fixture의 snapshot 비교도 별도 근거다. |
| 매 프레임 무제한 생성 | 3개 ImmediateMesh 재사용, particle/stroke/impact/voice/loot 상한 존재. bounded temporary 배열과 hull 계산 비용은 남는다. |
| 판정/표현 RNG 혼용 | 장식/효과는 별도 고정 RNG, 음향 variant는 순환 선택. 원본 CombatRun 핀은 유지한다. |
| 중복 이벤트/보상 | FX/audio seq 커서와 retry reset 존재. 전리품/정예 보상은 동결 코어03의 책임이다. |
| 자동 저장 변환 | 새 C2에는 사용자 저장 경로 로드/쓰기/변환이 없다. QA 파일 쓰기는 새 경로 + 기존 파일 거부다. |
| 원작 보호자산 혼입 | runtime70의 명시적 closure에 채택한 독립 생성 아트와 CC0 WAV만 추가했다. 거절한 run 시트/참고 영상/연구자료는 제외다. |
| 출력 덮어쓰기 | package03/tooling은 신규 출력 ID만 허용한다. 과거 실패와 후보02를 보존한다. |
| 합성 검사를 품질 통과로 확대 | headless158/159, GPU45초, 오프라인30FPS 영상, 수동 조작과 성능/청취는 문서에서 구분한다. |

발견한 비차단 음량 gain 문제는 `CODE-REVIEW.ko.md`에 기록했다. 소스 검색은 동적 실행의 모든 상태나 메모리 누수0을 증명하지 않는다. 커밋·업로드·사용자 저장 변경은 없다.
