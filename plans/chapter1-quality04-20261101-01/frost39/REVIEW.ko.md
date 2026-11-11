# 냉기39 소스 품질·금지 패턴 검토

2026-11-11. 신규 `chapter_elements_quality39.gd`와 냉기 shader4개만 읽기 검토했다. GPU·게임 실행은 이 검토에서 하지 않았으며 실제 시각 비교는 별도 검증 담당 결과와 root의 화면 판단을 따른다.

**소스 단계 판정: 차단 결함 없음.** 최종 시각 품질·성능 승인으로 확대하지 않는다.

## 확인

- 36효과를 상속한다. 새 cast cue는 실제 frost cast 이벤트의 seq/position/direction을 읽으며 피해·시전·빙결 판정을 소유하지 않는다. 이벤트 방향은 실제 Core37의 cast payload에 존재한다.
- frost39_cast를 부모 sync에 넘기지 않고 기존 stroke pool에서 잠시 분리한다. 부모의 알 수 없는 stroke를 arc로 취급하는 분기에서 from/to를 읽는 오류를 피한다. cue 수명은 playing 때 한 번만 줄고, 다시 합친 전체 pool은 기존96 상한을 유지한다. 부모 sync 중 새로운 stroke를 생산하지 않는다.
- projectiles/impacts/contacts의 INSTANCE_CUSTOM.g가 냉기 범위(.3,.8)인 인스턴스만 새 batch로 복사한다. 원본 transform의 basis를0으로 만들어 중복 기하를 숨긴다. 다음 부모 sync가 실제 코어 상태에서 원본 transform을 다시 작성한다. 새 batch 용량은 각각 원본 용량을 따른다.
- 접촉 .13초·명중 stroke .10초·impact .48초·상속 파쇄 fragment .48초를 유지한다. 파쇄 shard 상한128과 빙결의 실제 frozen_until 추적도 상속한다. 새 shader는 INSTANCE_CUSTOM의 age를 사용하고 벽시계 TIME으로 움직이지 않는다.
- 냉기 일반 cast의 기존5개 debris를 release cue로 대체하며 파쇄30개 dust는8개로 줄인다. 코어 난수·판정·지급·오디오·모델을 변경하지 않는다. 변경되는 난수는 표현 전용 debris RNG뿐이다.
- 신규 shader는 alpha 혼합·깊이 검사와 기존 실제 위치를 사용한다. frozen crystal/fragment 모양만 재조정하며 코어 좌표나 수명을 수정하지 않는다.

## 보존 및 한계

기존 후보38 FINAL-SOURCE-FREEZE의168개 파일을 현재 소스와 SHA256 비교하여 불일치0개를 확인했다. 기존36효과·코어·데이터·38조립이 변경되지 않았다는 근거다. 사용자 프로필은 이 검토에서 읽거나 쓰지 않았다.

새 batch4개와 매 프레임 transform/custom-data 복사 비용이 있으므로 최종 동적 성능 측정은 필요하다. 기존 인스턴스를 숨겼다는 사실이 draw call이나 CPU 비용이 동일하다는 뜻은 아니다. 전체 성능 검사와 모든 기능 검사를 이 단계에서 반복하지 않았다. 실제 화면에서 너무 약하거나 가려지는 표현은 시각 비교 후 조정한다.

이 검토에서는 소스 수정이 없었다.
