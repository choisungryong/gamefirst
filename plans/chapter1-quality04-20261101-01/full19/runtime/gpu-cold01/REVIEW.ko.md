# 후보19 실제 전체 GPU 종료 검수

실행은 terminal이다. gpu-execution actual_exit0/stderr0,397.7simsec/tick23862/3451처치/Lv12/epoch1/shatter840/cold-death823. 실제 패키지16과 mode/tick/kills/hero/growth/metrics/chapter/equipped/inventory/elite_reward_uid10개 모두 동일하다. 같은 전체 검사를 다시 실행하지 않는다.

27PNG 전부 IHDR1920×1080. 실제 run-001-frame-090에서 일반 적의 방향·골격/밝은 얼굴과 정상 냉기 전투를 직접 봤다. victory-after0.35에서 보스 세계 표시/죽음 진행과 냉기 사체 감소,1.60에서 실제 UID의 겨울의 심장 보상 카드를 직접 확인했다. 사망 자세와 최종 보상은 기존17 경로이며19에서 새로 만든 연출이라고 하지 않는다. 죽음 직후에도 주변 생존 적·투사체가 멈춰 남아 있어 더 강한 마무리 연출 개선 대상이다.

## 성능 관찰 한계 — 원시값 보존

external observer의 Engine delta44,714개 평균8.83345ms/p95 9.09091/p99 21.52167/max148.008,33.334초과349/50초과203프레임. 5초 초기 구간 제외/maxfps120/스크린샷 작업 포함이다. OS monotonic wall-clock per-frame 기록이 아니므로 최종 성능3회로 승인하지 않는다.

Performance.TIME_PROCESS는 캐시된 모니터를 매프레임 재표본한 값이다. 결과 평균75.685ms/p95 645.595ms는 위 frame interval과 불일치하므로 **실제 프레임 CPU 비용/평균으로 사용하지 않는다**. 모니터 갱신/캡처 정지와 표본 복제의 영향을 분리하지 못했다. raw stdout의 process_time 값은 지우거나 성공 수치로 고치지 않는다.

tree_exiting 콜백의 texture.get_size는2304×1296을 보고하지만 모든 저장 PNG의 실제 픽셀은1920×1080이다. 종료 시점 조회의 차이는 원인 미확정이다. 따라서 모든 프레임의 내부 렌더 크기를 이 콜백 하나로 확정하지 않는다. 최종 성능에는 OS wall clock과 실행 중 실제 Image/viewport 크기를 함께 기록하고 캡처 없는 고정 조건3회를 별도로 검증한다.

실제 정상 전체 전투/성장/보상/출처 증거는 유효하다. 수동·실청취·저장UI·최종아트/성능 검수는 미완료다.
