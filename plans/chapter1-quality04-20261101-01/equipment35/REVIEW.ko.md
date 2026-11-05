# 장비 그림35 실제 HUD 검수

네 슬롯 자체 SVG 그림을 HUD35의 _sigil에 연결한 격리 연구다. 제품34 assembly는 변경하지 않았다. hud01 정리 스크립트 RefCounted.free 오류는 실패로 보존, hud02 import/생성검사는 quiet 통과.

layout01 import/check/GPU 모두 exit0-stderr0. 정상 냉기 획득으로 첫승리23862tick까지 core만 진행한 뒤 1080p/720p 발견·승리보상·인벤토리 표시를 명시적으로 열었다. core snapshot 복원 동일. 6PNG 전부 직접 검수: 부적/로브 그림, 이름·능력치·버튼 겹침 없음, 목록 스크롤 영역 표시. 자연 발생 발견 이벤트나 실제 패키지·수동 플레이로 승인하지 않는다. 1080p 발견 사진의 상단 진행 안내는 명시적으로 playing으로 돌린 fixture 상태라 자연 승리 후 화면을 뜻하지 않는다.

다음 slots01에서720p 네슬롯/인위적 긴이름발견과 실제장비선택/스크롤 재구성 보존 검수 중. 제품 반영 전 해당 원시 종료 상태와 화면을 확인한다. 원34전체 GPU는 재실행하지 않는다.

## 네 슬롯·긴이름·스크롤 종료

slots01 import/check/GPU exit0-stderr0. 8PNG 전부 직접 검수. 720p 네슬롯의 서로 다른 그림이 읽히고 인위적 긴 이름은 말줄임되어 패널 밖으로 넘지 않는다. 실제 획득 장비의 비교 설명과 고유 부적의 냉기 능력 설명이 들어간다. 네 선택 모두 목록 최하단 스크롤값이 UI 재구성 뒤 동일. 전체 core snapshot도 원복 동일. 이 검사는 입력 자동화나 저장 지속성 검사가 아니다.

후보35 채택·패키징 시작. chapter1-before35-20261106-01에 후보34 assembly/project/preset/freeze와 사용자 저장 사본 보존. full35/ADOPTION.json의 이전 EXE/사용자 핀 확인. root assembly는 HUD27→35만 변경. 제품35 import/export/PCK 및 release smoke 결과는 종료 후 별도로 기록한다.

후보35 패키징 session39368 종료, PACKAGE35 COMPLETE. EXE SHA cd161021c38ea40bc19de49ab80d406c8f7884a3c6be887faaeec67d777ad797 /134132968bytes/runtime149-stage151-PCK272. import/export/PCK/30sim초headless/releasebehavior 통과, 이전EXE/사용자핀 재확인. 실제35 GPU UI/수동/실청취/최종focused 검수는 아직 미완료.
