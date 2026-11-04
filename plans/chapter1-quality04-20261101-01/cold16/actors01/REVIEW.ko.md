# cold16 일반 냉기 사체 정리 — 격리 화면 검증

새 `chapter1/view/chapter_actors_quality16.gd`는 Actor12를 상속한다. 실제 death 이벤트의 frost 원인과 현재 죽은 entity를 확인하고, elite 플래그/elite 종류를 제외한다. generation:id 키와 seq 중복 방지를 쓴다. 일반 냉기 사체는 푸른 색으로 0.025초 유지 후 smoothstep으로 0.22초에 투명해진다. 부모가 매 sync 계산한 기본 색/owner alpha 뒤에 한 번 적용하므로 색이 누적되지 않는다. paused/choice/inventory/equipment에서 시간을 멈추고 terminal에서는 진행한다. 기존 core/FX/HUD/보스/영웅 코드와 루트 조립은 변경하지 않았다. 기존 16 얼음 조각 .48초도 유지한다.

## 실행 근거

- `RESULT.json`: 전후 전체 core snapshot 시작/종료 동일, 후보14 freeze 전체 파일 및 EXE SHA 일치.
- seed90131, 기본 HP와 실제 획득 성장, 정상 full_pilot. 두 쪽 모두 cold16 규칙이다. tick3240까지 core 재시뮬레이션 → cosmetic 초기화 → 8초 GPU fixed60 짧은 재생. 14 규칙과의 비교가 아니다.
- 전후 import/check/GPU 각각 exit0/stderr0. 각 16장, 합계32 PNG.
- 8개 관측 검사 true: 실제 일반 냉기 사체 추적, 세 modal의 age/색 유지, terminal fade, 이벤트 재소비 중복 방지, core 불변, reset 초기화.
- `before-shots/shatter-02-after15.png`와 `after-shots/shatter-02-after15.png`를 직접 비교했다. 변경 전 중앙 위 갈색 사체 덩어리가 변경 후 사라지고 파편/생존 적/바닥이 드러났다. after06/after30도 확인했고 주황 위험 표시는 남아 있다.

이 결과는 대량 냉기 사체 겹침에 대한 제한된 개선 근거다. 최종 아트, 실시간 전체1장, 수동 조작, 음향 청취, 성능 통과로 확대하지 않는다. 살아 있는 적의 반복 자세와 뭉침은 별도 미해결이다. 후보16 EXE/루트 통합은 아직 하지 않았다.

## 다음 작업

정예/비냉기 제외 fixture의 종료 진단 결과를 별도 경로에서 확인한 뒤, 새 후보16 closure/백업/freeze/EXE 및 전체 정상 GPU 관문을 이어간다. 기존 normal01과 이번 actors01 출력은 재실행하거나 덮어쓰지 않는다.
