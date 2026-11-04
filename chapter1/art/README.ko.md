# 1장 아트 후보 — 2026-10-31

현재 아트는 독립 생성한 **2.5D PNG 스프라이트**이며, 리깅된 3D 모델이 아닙니다. 성인 비율의 다크 판타지 방향은 첫 플레이 후보로 승인받았으며 최종 C2 품질 승인은 남아 있습니다. 원본 GLB 제작 브리프는 대안 경로로 유지합니다.

- `terrain/cloister_ground_v01.png`: 돌·흙·이끼 바닥 알베도 후보. 실제 카메라에서 반복 이음새 확인 필요.
- `actors/{hero,walker,ranged,charger,elite}.png`: 각 4방향 × 4 이동 키프레임.
- `actors/{hero,walker,ranged,charger,elite}_actions.png`: 남쪽 기준 시전/공격 4, 피격 4, 사망 4프레임.
- 각 동명 JSON의 `frames[].region`은 가변 소스 사각형입니다. 단순 균일 셀 자르기를 사용하지 마세요. `frames[].feet`는 사각형 안의 발 기준점이며, `pixels_per_meter`와 프레임별 `texture`를 함께 적용합니다.
- `frames_by_direction`: south/east/north/west. `states`: idle/move/cast/hit/death, 적은 attack 별칭도 제공합니다.
- Godot Sprite3D의 양수 offset.y는 위쪽입니다. 뷰 담당자가 확인한 기준은 `(width/2 - feet.x, feet.y - height/2)`입니다.
- 전용 idle 클립은 아직 없습니다. idle은 이동 키프레임 하나를 유지합니다. 남쪽 외의 시전/공격/피격/사망 동작은 미제작입니다.
- `battle_mage_walk_4x4_v01.png`는 초기 레이아웃 증거로 보존했으며 런타임 대상은 `hero.png`입니다.

출처·원본 경로·전체 프롬프트·해시·크기·한계는 [ASSET-LEDGER.json](ASSET-LEDGER.json)에 기록합니다. 생성 원본을 보존한 채 프로젝트에 복사했으며 이미지 픽셀은 분석 스크립트로 수정하지 않았습니다. 생성 결과를 CC0 또는 제3자 라이선스 모델로 표기하지 않습니다.

검사: 모든 채택 이동 시트에서 큰 알파 연결 요소 16개, 행동 시트에서 12개를 찾았고, 선택 사각형 안에 이웃의 큰 연결 요소가 들어오는 픽셀은 0개입니다. 이 검사는 리깅·시간적 일관성·실제 카메라 접지 품질의 승인을 대신하지 않습니다.

세부 검사와 제작 보고서는 `plans/chapter1-c2-20261031-01/art/`에 있습니다.

