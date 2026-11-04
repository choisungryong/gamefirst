# 적 탄환22 — 제품 미연결 시각 연구

실제 후보21 네이티브 도전에서 관찰한 작고 어두운 적 탄환의 대비를 개선한다. comet_hostile22.gdshader는14셰이더의 hostile branch만 변경했다. 밝은 황금색 마름모 중심은 paid projectile 위치에 맞추고 짧은 주황 꼬리로 진행 방향을 읽는다. 아군 분기/원래384한도 배치/transform/크기/위치/피해 판정은 그대로다. chapter_elements_quality22.gd는20상속 setup에서 같은 배치의 shader만 바꾼다. root21 scene/view는 미변경,22EXE 없음.

compare01: 정상6500tick에 hostile0/friendly11이라 실패. assert 후종료 미도달, 명령 확인후 특정GPU PID25376종료/exit4294967295/stderr164. raw/stage/PNG/FAILED-RESULT 보존. 품질 통과 아님.

compare02: 정상정책 중900tick이후6m내 적 탄환6개이상인 최초1079tick에서 물리만정지. 실제hostile15/전체17. 동일 camera/core/batch에서 shader swap전후 actualPNG1920×1080 직접확인. 완전core동일true/종료0/stderr0. 논리viewport1600×900이며 실제PNG는1920×1080. 정적 비교이지 실시간 플레이/성능 아님.

replay01: 정상900tick 재구성후 fixed60 GPU10sim초/1500tick. maxhostile17,샷1021tick14/1201tick9/1381tick3. 독립정상정책과종료전체core동일true/종료0/stderr0. 실제PNG3장 직접확인: 밝은 중심과 방향꼬리가 바닥과분리되고 아군서리창/발사예고와 구별됨. 정상정책 부분재생이며 수동전체/최종1080p3run/동영상 실청취 아님.

원21 freeze모든핀유지. 기존사용자저장/후보/성공실패증거보존. 제품연결은 다음공간개선과 함께판단. 정적/동적 셰이더시각검수가 첫장완성은아니다.
