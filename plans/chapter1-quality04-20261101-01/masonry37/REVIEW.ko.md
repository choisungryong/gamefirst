# 후방 석재37b 미연결 검수 · 2026-11-06

제품은 아직36(Core36/World31d/Actor36/HUD36/FX36)이다.37와37b는 별도 연구 소스이며 root assembly/freeze/EXE에 채택하지 않았다.

## 이전 상태와 보존

compare01은31d 대37 chamfer 비교를 종료했고 core/anchors/batch-count/held가 모두true였다. 화면 품질 판정은 미완료로 기록돼 있었다.37b의 compare02는 증거 디렉터리가 비어 있고 stage에는4파일만 있었다. charger.png는0바이트인 부분 복사 상태였다. 실행/검사/결과 증거가 없으므로 성공으로 취급하지 않는다. 해당 부분stage를 수정하거나 삭제하지 않고, compare03/SOURCE.json에 당시 파일 해시를 보존해 작업 전후 동일성을 확인했다.

compare02 러너는 기존 디렉터리 부재를 요구하고 구형 USER-PRESERVATION-ADDENDUM01을 참조한다. 현 default36은 수동 장착으로 revision2가 됐으므로 그대로 재실행해서는 안 된다.

## compare03 수행

새 run_masonry37_compare03.py와 고유 stage를 작성했다. 기존36 staging-manifest의 모든 파일을 검증·복사하고37/37b와 고유 observer만 추가했다. 최신 USER-PRESERVATION-ADDENDUM02 핀, 제품36 FINAL-SOURCE-FREEZE, compare02 부분stage를 전후 대조했다. 전부 불변이다. 사용자 저장은 profile-off로 읽기/쓰기 모두 비활성화했다.

import/check/native31d/native37b 모두 exit0/stderr0. source36 정상번개 seed90131의9000tick 상태를 동일하게 계산해 동결했고,3개 후방 점검 카메라와 실제 영웅 카메라 총4장씩1920×1080을 저장했다. snapshot 전체/석재 위치·변환/배치 instance 수/캡처 전후 core 불변이 모두true다. 원시 RESULT와 COMPARISON은 compare03 하위에 있다.

37b 네 화면을 직접 확인했다. 안쪽·바깥쪽 아치띠가 추가돼 기존의 단순한 각진 윤곽에 층과 모서리 깊이가 생겼다. 그러나 큰 돌 표면의 어둡고 매끈한 청회색 질감은 밝은 이끼·조각이 있는 기존 기둥과 여전히 차이가 있다. 기하 개선 증거이며 최종 석재 미술 품질 완료 판정은 아니다.37b를 채택한다면 해당 제한을 명시해야 한다.

## 제한된 정적 비용

마지막 영웅 카메라/동일9000tick 동결 상태에서2초 워밍업+10초 monotonic process-frame 벽시간을 각1회 측정했다. 측정 중 이미지 읽기/저장 없음.31d는5103개 표본 p95=2.476ms/p99=2.786/max=5.597,37b는5139개 p95=2.462ms/p99=2.851/max=12.344였다. 과도한 지속 비용 증가 증거는 보이지 않지만 최대값은 한 번 더 높았다. 정적 장면의 제한 비교이며 동적 최종 focused3회 성능이나 고정60FPS 증거가 아니다.

## 다음 판단

최소 후속37c를 만든다면37b의 geometry/위치/2배치를 유지하고 후방 두 석재 material만 대상으로 기존 flagstone+soil texture를 사용하는 공간 질감·옅은 광물/이끼색 변화를 비교할 수 있다. 기존 rear material에도 이미 flagstone world-triplanar texture가 있으므로 단순 texture 누락 문제로 설명하면 안 된다. 조각기둥의 atlas는 구워진 원근·음영이 있어 석재에 무조건 재투영하지 않는다. 외부 에셋을 추가할 필요는 없다.

최종 formal3회는 최종 채택한 단일 후보 EXE에서 실행해야 한다. run_performance29_v2.py와 frame_probe_render23.gd 패턴을 새 경로에 복사하되 후보 경로/스크립트 식별을 갱신하고 파일 핸들·view cleanup을 명시한다. native menu focus/start 후10초warmup+60초 sample,각 armed frame focus/1920×1080/scale1/MSAA2/Forward+/VSyncoff/uncapped를 확인한다. autostart/fixedfps/movie/ignorefocus/측정 중 캡처는 사용하지 않는다. 프로필은 off, 기존23/29/36 최신핀은 전후 검증한다.3회는 같은 EXE 해시여야 한다.

모든 compare03 프로세스는 종료했다. 전체 수동 플레이·실청취·기본저장 경고 원인분리와 별도 범위다.

## 37c compare05 · 후방 재질 개선 검수 종료

compare03 정적 비용은 같은 시간 다른 headless 진단이 실행됐을 가능성이 확인됐다. 따라서 격리된 비용 통과로 취급하지 않고 탐색값만 유지한다. 확정 비용 측정은 CPU/GPU 단독 예약 뒤 별도 실행해야 한다.

37c는31d를 직접 상속하고37b RefCounted 인스턴스를 기하 생성 helper로만 사용한다. helper의 setup은 호출하지 않아 씬 노드·root 소유권이 없다. 후방 RearMasonry22/RearArches22 두 batch만 새 shader material을 적용하고 나머지 배치는31d 원래 경로를 그대로 사용한다. 기존37/37b의 전체 배치 색·재질 변경이 shadow proxy로 전파되는 것도 피했다. root assembly에 채택하지 않은 연구 파일이다.

새 shader는 기존 flagstone/soil 두 texture를 world-space triplanar로 사용하고 낮은 강도의 광물·이끼색 변화와 거친 질감을 넣었다. Godot4.5 spatial shader 공식 built-in/sampler 문서를 실제 읽고 기존 chapter_ground shader의 문법을 재사용했다. 외부 에셋이나 새 이미지 파일은 추가하지 않았다.

compare04는 import/check quiet 통과 후 native37c 중 C드라이브 용량 부족 대응으로 종료했다. view-0.png 한 장만 남았으며 결과/시각 승인으로 사용하지 않는다. 원시·부분stage는 보존했다. 캐시는 사용자 용량 정리로 D아카이브로 옮겨졌으나 원본 소스는 그대로다.

compare05는04 SOURCE manifest와 현재37c 두 소스의 해시를 검증한 뒤04stage를 재사용했다. 통째로 새 stage를 복사하지 않았다. 필요한 import cache만 재생성했다. 새 출력05에 native37c 네 장을 캡처하고 완료된37b compare03를 기준으로 비교했다. reimport/native 둘 다exit0/stderr0. 전체Core36snapshot/모든anchors/batch AABB·surface·instance 수/카메라기록/core불변이 모두 동일하다. 두 shadow proxy 재질이 원래 roughness .97/specular .5/흰 albedo인지 실제 확인했다. 제품freeze와 최신 사용자핀도 불변이다.

37c 네 이미지를 모두 직접 확인했다.37b의 매끈한 청회색보다 불규칙한 광물색과 옅은 회녹색 풍화가 생겼고 아치띠 깊이는 유지된다. 불빛이 있는 회랑에서는 따뜻한 갈색을 유지하며 초록색으로 전체를 덮지 않는다. 성소 윗면에는 옅은 이끼색이 읽힌다. 기존 장식기둥보다 조각 밀도는 낮지만 주위 지면·벽과 연결되는 질감은 개선됐다. 제한된 후방 석재 개선 후보로 채택 검토할 수 있으나 최종 SACRATA 아트 완료가 아니다.

compare05는 비용을 측정하지 않았다. 독립 코드검토와 전용 비용 슬롯의 검사 후 채택 판단을 한다. 모든05프로세스는 종료했고,04원시/02부분파일/03성공 증거는 유지했다.

## cost01 · 전용 슬롯 상대 비용 확인

root가 CPU/GPU 단독 슬롯을 명시적으로 배정한 뒤04stage를 재사용했다. 신규 stage 복사·import·이미지 파일 저장 없이 고유 cost01 observer를 실행했다. 동일 Core36 정상번개9000tick/영웅 카메라를 동결하고37b→37c 순서로2초워밍업+10초 sample 각1회 측정했다. raw CSV에 monotonic elapsed/interval·focus·draw call을 보존했고 Python으로 표본 수/합계/해시/p95를 별도 재계산했다. readback은 워밍업 전·샘플 뒤에만 수행했다.

check/native37b/native37c 모두exit0/stderr0. 원본소스·04stage 기존manifest·사용자 최신핀 불변. 전체snapshot과설정동일/실제1920×1080/모든측정frame focus가true였다. root와GPU 프로세스는 모두 종료했다.

| 정적 단일 표본 | 표본수 | p95ms | p99ms | maxms | draw중앙값 | unfocused |
|---|---:|---:|---:|---:|---:|---:|
|37b|5257|2.379|2.600|9.450|273|0|
|37c|5172|2.427|2.669|8.777|273|0|

37c의 p95는+.048ms(약2.02%),p99는+.069ms이며 draw 수는 같다. 큰 지속적 비용 증가를 보이는 결과는 아니지만 상대적인 한 쌍의 정적 회귀 점검이다. 최종 동적 focused3회/고정60FPS 승인으로 사용하지 않는다. 자동 허용률 임계값을 임의로 만들지 않고 채택은 root의 품질·비용·독립검토 판단에 맡긴다. 원시는 cost01/COMPARISON.json,각 arm RESULT.json/frames.csv/launch/execution/log에 있다.
