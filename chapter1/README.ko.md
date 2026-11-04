# 새 1장 개발 경로

기준은 `plans/chapter1-preproduction-20261031-01/`의 분석과 제작 도감이다. 이 경로는 기존 Baseline/Expedition과 별도로 개발한다. 현재 진입 scene·기존 소스·내보낸EXE·사용자 저장은 바꾸지 않는다.

첫 구현은 성장 코어다.

- `data/growth.json`: 독립3계열·4랭크·패시브 선행조건·진화 효과 정의. 피해raw는1/256단위, 반경cm, 주기는60Hz tick이다. 수치는 신규 초안이며 참고작의 복원 공식이 아니다.
- `core/growth_catalog.gd`: 전체 검증 후 원자적으로 교체하고 detached 사본만 노출한다.
- `core/run_growth.gd`: XP/레벨·유효3지선다·가중 비복원 추첨·주력 진화 도달 경로·선택 token/epoch·실제 효과 정의를 소유한다.
- 패시브는 현재 진화 선행조건 역할이다. 별도 보너스·각 기술 쿨다운 스케줄러·월드 타격·VFX·음향·저장·게임 화면은 아직 연결하지 않았다.

`configure(document,primary_skill,run_seed)`는 새 런을 시작하고 이전 offer token을 무효화한다. `award_xp(amount)`로 선택 권리를 얻고, `next_offer()`의 token/card ID를 `choose(token,card_id)`에 제출한다. 같은 offer를 반복 열어도 RNG가 전진하지 않는다. 상태 조회는 `snapshot()`과 `effective_skill(id)`를 사용한다. 이번 코어에는 원본 사용자 저장 I/O가 없다. snapshot은 디버그 조회이며 검증된 저장/복원 형식이 아니다.

검증 실행:

```powershell
& 'C:\Project\rea-tools\godot-4.5.1\Godot_v4.5.1-stable_win64_console.exe' --headless --path 'C:\Project\d2r-combat-baseline' --script res://chapter1/tests/test_growth.gd
```

다음은 실제 전투 스케줄러·새 성장 모달·XP 회수·장비 효과를 연결하고, 최종 자산 제작 경로와 함께90초 구간으로 검수하는 것이다. 코어 테스트 통과를 제품 품질·90초 완성·1장 완성으로 표시하지 않는다.
