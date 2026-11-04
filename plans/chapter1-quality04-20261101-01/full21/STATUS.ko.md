# 후보21 — 세 구역 클릭 수정·원거리/돌진 골격 통합

EXE `builds/chapter1/chapter1-full-candidate-20261103-21/AshenCloister-Chapter1.exe`,SHA256 `3775b55ab2f52d03c844b80c1392251669bf2ac96e5bb43e8bda645189763000`,130042864bytes/runtime116/stage118/PCK210. core16/World18/HUD20/FX20 유지,Actor21. ChapterOne.tscn이 새 chapter_one_input21.gd를 쓰고 기존 chapter_one_view.gd에서 Actor preload만21로 바꿨다. main/preset은 Baseline, 패키지 저장은 Quality21 namespace. 원20 scene/view/project/preset은 `C:/Project/game-research/implementation-backups/chapter1-before21-20261103-01/` 보존.

## 실제 입력 수정

기존 full chapter가 대표장면의 [-18.8,18.8] 좌클릭 clamp를 그대로 상속해2·3구역의 클릭 목표가 첫 구역으로 돌아갔다. 새 full controller는 core의 열린 구역/통로 `_clamp_point`를 사용한다. 대표 Chapter1 scene은 보존했다. input21/fixture02는3구역×3목표+inventory차단/core복원/legacy비교14검사 quiet,legacy7경우가 잘못된 목표였음을 확인했다.01은 검사true이나종료ObjectDB경고124bytes/helper실패이며 보존했다.02 helper는 ready scope를 반환한 뒤 종료하고 verbose로 확인했으며 장기 누수 해결 주장과 구분한다.

실제 패키지 native-input01은 정상 획득 빌드의9000/16000tick 장면을 재구성하고 물리 루프를 멈춘 입력 fixture다. 실제 마우스 클릭 뒤 제품 `_move_input`으로30정상 core step을 적용했다.2구역 목표x52.20/영웅45.24→47.60,3구역 목표x105.06/영웅98.83→101.05,둘 다 실제선택과기대한목표일치/방향이동true,exit0/stderr0. 기존clamp는둘다x18.8이었다. 실제native입력 증거이며 수동전체/실시간 전투가 아니다.

## 원거리·돌진과 비용

ranged/charger도 기존 허가73골격을 사용한다. ranged는 키큰청록·긴 지팡이,charger는 낮고넓은몸체/실제dash walk/회복idle. 투사체·돌진 피해나 core를 바꾸지 않는다. roles21/replay04 정상6500→7700tick 전체core동일/quiet에서 지팡이손위치·실제dashwalk/recoveridle을 검수했다. 이후 성능용으로 지팡이 shaft/crystal을1surface공유mesh/정점색/작은절차적emission map으로 합쳤다. 먼3m 밖 이동만20Hz,가까운적과공격/돌진은기존빈도. pose가같을때손bone계산을재사용한다. 최종fixture02의23검사/quiet에서freeze/modal/staffalpha/reset/paidpose/core복원을확인했다.

합성129walker/33ranged/18charger,실제PNG1920×1080/MSAA2/vsync off/uncapped,120warmup+360frame. OS monotonic 원시 frame/actor callback시간을 저장했다. 후보20 평균13.536/p9514.603ms/draw467,최초21 평균17.847/p9521.350/draw599. 최적화21 평균14.855/p9516.694/draw533,actor callback평균9.853ms다. 원20 기준을 재사용했고 같은검사를중복하지않았다. 원시표본·전후PNG 보존. 이는합성 presentation부하이며 정상core계산·전체FX·최종3회가아니다. 최적화PNG에서 역할·지팡이형태를직접확인했다.

패키지 import/export/PCK/입력probe/30simsec정상정책 성공. 그30초10상태는20과같다. 원17세주력/원19냉기전체는core불변범위로상속하며21전체GPU라고부르지않는다. 기존14/16/17/17b/18/19/20/21과모든성공·실패·사용자저장보존.

독립감사28개가source/stage/EXE/PCK/기존후보보존/검증소스와패키지대응/실제후반입력/30초10상태동일을확인했다. 모든게임실행terminal. 서버8781은 재개시종료돼full20/book-v13/browser02의 새 PID19884로127.0.0.1에재시작했다. 최신도감full21/book-v14는22HTML/541refs/missing0,실제브라우저22×1440/390폭44case h1/overflow통과/표지직접확인. 다음은네이티브전체한판으로체감문제를찾고 공간·타격개선을이어간다. 실청취/기본user저장/최종1080p3회도남았다. 목표active,2·3장미착수.


## 추가 — 실제 도전과 미연결22 연구

manual01·02 실제조작은18.90/38.07sim초에패배,exit0/stderr0. full21/runtime/MANUAL-REVIEW.ko.md에입력/지연/검증범위를기록했다. 적탄환22는미연결시안이며정적02/동적01에서core동일/quiet/실제화면검수,01실패보존. hostile22/REVIEW.ko.md참조. 최신도감v15는23페이지/590refs/missing0,실제두폭46case통과. 원21제품freeze유지/22EXE없음. 다음은공간깊이개선. 목표active.
