# 정상 속도 연속 영상 · 원시 기록과 한계

normal-film01은현재27source기반/정상획득화염16000tick체크포인트부터4sim초연속렌더다. control은Actor25b,after는Actor28. 각별도stage에서Godot MovieMaker60fps로프레임을연속기록하고ffmpeg로MP4인코딩했다. 이전motion02/film01처럼8시점만길게보여주는샘플영상과다르다. 오프라인고정step이므로실시간GPU성능이나수동입력증거는아니다.

두실행모두import/GPUexit0-stderr0,원core독립기준동일/끝16241tick. after에서280피격혼합. control/after의관찰1.0초는16060tick/같은hero좌표,3.0초는16181tick/같은hero좌표였다. MovieMaker영상은control245frames/4.083333초,after246frames/4.1초,모두60fps/1280×720다. AVI원본과게임오디오/MP4보존. 오디오실청취승인아님.

analysis01은동일총프레임수라는가정으로실패했다. analysis02는raw decoded framemd5로마지막동일이미지반복수를제외하면맞을것이라는가정도실패했다. 두분석폴더·중간키프레임·probe·md5·스크립트모두보존하고통과결과로승격하지않는다. chapter_view.gd는QA종료플래그후OS시계150ms오디오해제를기다리며,이기간render프레임수변동가능성은있으나이번자료로차이가오직그때생겼음을증명하지못했다. 영상을임의절단하거나프레임삽입해검사를맞추지않았다.

따라서두영상은각각정상속도연속source영상이며정확한프레임동기전후비교로승인하지않는다. analysis01의1초/3초전후4PNG를직접검수해같은상황에서인물·탄막·구조가보이는것은확인했다. 전체영상직접재생검수·자연스러운반동최종판정은아직이다. raw RESULT scope는과거10sim초helper문구를물려받았으므로이번4sim초영상길이근거로쓰지않는다. SCOPE.json의실제실행인수/ffprobe/tick를우선한다.

별도CPU대조profile-control01/after01은같은정상화염2800→3400tick/599표본각1회. actors평균1.871573→1.960958ms/최대4.075→4.261ms,after44피격혼합.양쪽224생성112재사용/core동일/quiet.평균추가약0.089386ms이며실시간프레임페이싱·최종성능승인아니다. process최대56.077→27.130ms차이로성능개선을주장하지않는다.

다음은frame→core tick를명시적으로기록한연속캡처와공격windup→release→recover전후방향검수다. 현재제품27유지/Actor28미연결이며기존녹음·저장·후보불변. session25831 CPU두건/1482 연속영상두건모두terminal,같은검사재실행금지.
