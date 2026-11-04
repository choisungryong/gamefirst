# 1단계 정의 데이터 계약

게임 실행의 정의 원본은 `game_data/catalog.json`이다. `game_catalog.gd`는 JSON 구문, 버전, 타입·정수성·유한 범위, 단위·ID 참조, 출처 상태와 basis ID, 초기 좌표 범위를 모두 검증한 뒤에만 전체 카탈로그를 교체한다. 실패하면 `errors`를 제공하고 기존 카탈로그를 유지한다.

- `load_file(path)` / `load_text(text)` / `replace_document(value)` → 성공 여부.
- `snapshot()` / `definition(group,id)` → 깊은 복사본. 호출자가 정의를 바꿔 원본이나 다른 개체에 전파할 수 없다.
- `legacy_profile()` → 기존 `params` 소비 경로를 위한 파생 호환 형태. 기존 `evidence-profile.json` 파일을 읽지 않는다.
- `validate_research(value)` → 선택한 원문 claim의 메타데이터 형식 검사. 출처 파일 내용의 진실성을 이 함수만으로 입증하지 않는다.

현재 지원 범위는 health/mana의 scale256, caster1, skill1, projectile1, 적1이며 확장형 RPG를 구현한 것은 아니다. scale256과 모든 실행 규칙은 독립 설계값이다. `basis`는 검토한 클래식 계산·UI/영상 근거를 가리키며 현재 D2R 네이티브 함수 복원을 뜻하지 않는다. `evidence_index`의 연구 파일 경로는 출처 위치이며 게임이 열거나 요구하는 런타임 경로가 아니다.

기존 `baseline_sim.gd` 상수 MANA_COST 등은 초기40/109검사의 호환 fixture 별칭으로 남아 있다. 실제 실행은 검증된 카탈로그에서 읽은 `mana_cost_raw`, `damage_min_raw`, `damage_max_raw`, `startup_ticks`, `mana_max_raw`를 사용한다. 새 밸런스 프로파일은 이 instance 값과 정의를 검사해야 하며 기존 별칭을 데이터 원본으로 삼으면 안 된다.

`research/phase1-claims.json`은 실제 표의 raw8개를 보존한다. 빈 칸·음수 Picks·알 수 없는 단위는 그대로 남기며 의미/정규화는 미확인이다. 0의 구분은 합성 fixture도 검사한다. 게임 export에는 연구 폴더, 원래 evidence-profile, 변환기/테스트를 포함하지 않는다.

`tools/convert_legacy_profile.py`는 한 번의 명시적 이행 도구다. 기본 원래 profile과 검토된93847 표3개의 고정 SHA를 확인해 새 JSON을 만든다. 실행 정의가 바뀐 뒤 무심코 다시 실행하면 이행 시점의 밸런스로 돌아갈 수 있으므로 자동 동기화에 사용하지 않는다. 다른 빌드/표 바이트는 거부하며 지원 확장은 별도 검토해야 한다.

검증 예: `--headless --path <project> --script res://tests/test_catalog.gd`. 기존40/109검사와 독립1단계 검사는 별도 실행한다. 테스트 수는 원작 규칙 검증 개수나 최종 게임 품질을 의미하지 않는다.
