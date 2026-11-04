# 실제 기본 user:// 저장·재실행·장비 적용

기존QA절대경로테스트20과달리,실제23 EXE가원래product profile.configure() 기본값 user://chapter-one-profile-v1.json을사용했다. configure/path override없음. preflight는profileclass를사용하지않고실제custom namespace AshenCloisterChapterOneQuality23와물리경로 C:/Users/twins/AppData/Roaming/AshenCloisterChapterOneQuality23/chapter-one-profile-v1.json에파일이없음을확인했다. 기존사용자프로필을읽거나이동해시험데이터로쓰지않았다. 새테스트프로필·revision도삭제하지않고default-profile-preserved.json에핀보존한다.

- default-save01: helper변수namespace가GDScript예약어라parse/exit1/stderr413,실제profileconfigure와GPU시작전실패. 원본두helper/raw로그보존. 제품저장실패가아님.
- default-save02: 변수명수정,외부nativehelper를check-only후실행. 실제기본profile로정상획득빌드23830tick재구성뒤제품정상마지막전투와보상. tick23862/3451처치/Lv12/34장비/완료1/rev1실제저장. 종료0/stderr0. .35/.90/1.60초캡처와보상저장완료화면. 정상전체를재구성한부분재생이며수동전체아님. run-frame-150등기존자동capture이름은bootstrap후지연캡처라그과거시각의실시간증거로쓰지않는다.
- default-reload01: 새실행rev1/34읽기. 실제Sky UI보관함→수확의유리반지→다음도전장착으로ring storage4/rev2저장. 실제냉기시작→I장비창에서◆반지/피해+12%/최대HP-10/회수+.7m확인. 시작실제HP110/110확인,관찰지연후I시40/110이며무피해시험이라고하지않는다. 게임은inventory에서AltF4종료/quiet.
- default-reload02: 다시새프로세스rev2/34/보관함반지◆유지. 실제냉기시작→I장비창에서동일효과/최대HP110/적용ring UID1·storage4. 종료0/stderr0,파일전후byte같음. 프로필에추가완료/아이템을기록하지않음.

nativeUI는실제클릭·I/AltF4를사용하며helper는로그/상태·캡처만읽었다. 첫save02만정상정책ending용재구성과pilot를쓴다. 모든UI원시입력로그/성공·실패/observer원본/새프로필rev1·rev2복사/캡처보존. 보조ui-NNN PNG는상태변경후다음draw이므로파일순번만으로화면을단정하지않고직접확인했다(두번째재시작◆는ui003,장비는state-0004-inventory). 기본저장행복경로는실제증명됐지만동시쓰기·디스크고장·모든복구경로까지승인한것은아니다. 수동전체/실청취/최종성능/첫장완성아님.
