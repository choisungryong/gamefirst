# 바닥 장비 이름26 · 2026-11-04

기존25b 실제전체PNG에서근처장비이름이약7px로작게읽히는문제에대해chapter_elements_quality26.gd를만들었다.22 FX상속/기존실제drop빛기둥·8m표시범위·core드롭/회수규칙유지. 같은Malgun Gothic SystemFont로논리화면기준nominal15px(1920×1080에서약18px)로보이게크기조정. 긴이름모두표시/검은외곽선/3D높은drawpriority로적·기둥가림방지. rare→magic→common/UID순배치,이름겹침시같은행격자로수직간격조정,이동한이름에얇은원드롭연결선. 글자측정값은노드생성때캐시하고pixel_size의미미한동일값재설정은피한다. 수집은원래core만수행하며이름은입력을가로채지않는다.

API확인자료: https://docs.godotengine.org/en/4.5/classes/class_label3d.html (font_size/pixel_size/outline/render_priority/no_depth_test). no_depth_test만으로나중에그려진투명적가림을막을수없어priority도지정했다.

fixture01:29검사기술통과/quiet이나normal16000tick근처drop0개라전후검증이비었고,밀집12개그림의하단이름가림/낭비된행간이보였다. 6PNG/raw/source원본stage모두보존,채택근거로사용하지않음. 수정후fixture02:실제normal최초근처drop있는16143tick/실제UID30,원래속성대비커진글자정적전후및복제12-item밀집3해상도.30검사/quiet/전체원core복원,actual1920×1080·1440×810·1280×720의이름크기/서로겹침없음/화면범위/원빛기둥위치확인. 실제6PNG중normal전후/밀집세해상도5장직접검수(밀집before02는아직직접검수표시안함). before는같은시안의label속성을25b기본값으로되돌린표시fixture이며별도25bEXE검사가아님.

replay01은helper의tab/space혼합parse오류checkexit1/stderr280로GPU전종료. source/runtime25b결함이아니다. 실패stage/raw/helper보존,새02에서전체들여쓰기정리. replay02는정상냉기16000→16840tick/14sim초fixed60GPU/전체core독립기준동일/quiet/원dropnode소유오류0/최대표시이름1개. 이구간pickup은0개라회수성공증거로사용하지않음. PNG4장보존/아직직접검수미완료.

collection01은정상획득냉기16143checkpoint뒤실제근처UID30드롭으로일반이동명령을보내회수. 위치이동/장비grant없음.16200tick회수/16260tick종료,117개동일이동명령을재현한독립전체core동일/이름·빛기둥노드제거/quiet. 전후실제1920×1080 PNG2장직접검수. 시뮬레이션입력fixture이며native수동전체나normalpilot전체라고하지않음.

이표시개선만full26에개발채택하며Actor26피격연구는미채택/기존Actor25b유지. core16/World22/HUD23/Input21도유지. full26패키지상태와새실제검증을먼저확인한다. 모든과거후보/성공실패/사용자저장보존. 정상수동전체/실청취/최종1080p3회/공간·전투·발견최종품질은계속검수한다.
