# 원거리·돌진21 — 후보21 통합

후속 최적화는 지팡이 shaft/crystal을 공유1surface로 합치고 먼3m밖 이동만20Hz로 갱신하며 같은pose의 손bone 위치를 재사용한다. 공격/돌진/가까운적의빈도는유지한다. mixed129walker/33ranged/18charger의 실제1080p/MSAA2/uncapped/OSmonotonic120warmup+360frame 비교에서 최초21 평균17.847/p9521.350ms/draw599를14.855/16.694/533으로줄였다. actor callback평균9.853ms.20기준은13.536/14.603/467이며 재실행하지않았다. 최종fixture02의23개freeze/modal/paid/staffalpha/reset/core복원검사도quiet통과. 합성부하이며 정상전투·전체FX·최종3회승인아님. 최적화된PNG에서역할과지팡이형태를확인했다. 현재제품은21이고이하20미연결표현은연구당시역사기록이다.

후속03은 완료/quiet/전체core동일이고 dash=walk,recover=idle로 잘못된 두 번째 타격 표현을 제거했다. 그러나 실제 ranged-recover의 지팡이 투영 길이가13.67px뿐이고 화면에서도 잘 드러나지 않았다. 손목 방향을 함께 따라 지팡이가 시야 방향으로 누운 것으로 판단해, 실제 손 bone 위치는 따르되 shaft 방향은 actor의 수직을 유지하도록 바꿨다.04는 완료/quiet/전체core동일/dashwalk·recoveryidle 검사 통과이며 지팡이 투영 길이51.31px다. 실제 ranged-recover PNG에서 긴 shaft와 결정이 몸체 위로 보이는 것을 직접 확인했다. 제품 통합·혼합 군중 성능/빙결·reset fixture는 남았다.

제품은20이며21 EXE는 없다. Actor21은 기존73골격/한 surface batch를 재사용해 ranged는 가늘고 긴 몸체·지팡이,charger는 낮고 넓은 몸체·실제 dash walk/전방 기울기로 구분하는 시안이다. 기존 core의 투사체/돌진 궤적과 피해를 바꾸지 않는다.

replay01은 helper e의 Variant 타입 추론 오류로 check exit1/stderr277/GPU 미시작. 원본 보존.02는 정상 frost90131/실제 성장/defaultHP를6500tick까지 재구성한 뒤20초 fixed60GPU,최종7700tick 전체 core가 독립 정상정책과 같고import/check/GPU0/stderr0다. 실제 ranged fan release6540/.157과charger dash6764→recover6796을 관찰했다.

실제 field3/ranged-recover/charger-dash PNG를 봤다. 역할별 골격 동작은 연결되지만 지팡이가 너무 가늘었고, charger recovery가 부모 slam을 다시 재생해 실제 두 번째 공격처럼 보이는 문제가 있었다.02 raw dash pose 메타의 idle도 실제 override walk와 달라 정확하지 않다.

이를 보완해 지팡이 두께/결정을 키우고, dash 메타를 실제 walk로 맞추며 recovery를 idle로 바꿨다. 역할 색도 약간 조정했다. 새 helper는 지팡이의 실제 투영 길이를 기록하고 실제 dash=walk/recover=idle을 검사한다. 이 변경은 replay03에서 검수 중이며 완료로 주장하지 않는다. 기존20 root freeze와 모든 연구 stage/log/PNG를 유지한다.
