# 뒤 구역의 좌클릭 목표 제한 수정

기존 full chapter는 대표장면의 [-18.8,18.8] target clamp를 상속해zone1/2의 목표를 첫 구역으로 보냈다. 별도 chapter_one_input21.gd에서 열린 모든구역/통로의 core `_clamp_point`를 사용했다. 대표 Chapter1 장면/기존20 PCK/소스는 보존했다.

fixture01은14검사true/엔진exit0이나종료ObjectDB경고124bytes로helper실패. stage의 원시 결과를 별도 파일에 복사 보존한다. helper 종료를 ready scope 밖으로 옮기고 verbose fixture02에서14검사/exit0/stderr0. 장기누수 문제의 확정해결로 확대하지 않는다.3구역×3목표,inventory 입력차단,전체core복원,legacy7실패를 확인했다.

실제21 native-input01은 정상획득빌드9000/16000tick을 재구성하고물리루프를멈춘fixture다. 실제마우스이벤트를받아제품컨트롤러로30정상corestep을적용했다.2구역x52.20/영웅45.24→47.60,3구역x105.06/영웅98.83→101.05,둘다목표일치/방향이동true/exit0/stderr0. 이전clamp면두목표모두18.8이다. 실제캡처/원시입력/선택좌표를보존했다. 이는네이티브입력의연결증거이며 수동전체/실시간전투/성능검사가아니다.
