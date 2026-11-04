# 미연결 Actor26 피격 상체 동작 연구 · 2026-11-04

현재제품은25b그대로/26EXE없음. chapter_actors_quality26.gd는25b상속/기존허가모델의사용하지않던hitclip상체9bone(가슴3/어깨2/팔2/목/머리)을0.2초동안최대.55로혼합한다. 다리와공격예고/돌진/회복·사망우선순위유지,빙결과modal은전체표시포즈정지. 실제피격tick만사용/core수치불변. 초기13pose캐시를만들어피격마다AnimationPlayer를추가샘플링하지않는다. 20Hz부모가포즈재생을건너뛰는프레임에서도이전혼합의base9pose를먼저복구해누적변형방지. ranged지팡이는혼합/복구후새Hand.R위치를따른다. poolcheckout시26임시metadata도기존규칙으로제거된다.

fixture01은42개headless검사quiet. 이후지팡이가피격후손을따라가도록보완/expire시weightmetadata제거.원source는fixture01 stage에보존. fixture02는43개quiet:4역할별상체변화/하체동일/빙결·4modal정지/공격우선/만료복구/reuse정리,원전체core복원,13sample9bone/지팡이hand일치. 표시fixture이지normal/visual증거아님.

replay01은새26소스/정상화염90131획득16000tick재구성후10sim초GPU→16600tick,648hitblend/전체core독립기준동일/quiet. 실제1080p4PNG모두직접확인. 일반카메라에서반응은작고자연스러운수준이며타격감완성으로승인하지않음. 부분재생이며제품/수동/전체/성능아님.

compare01은같은26표시기에서새혼합off/on,복제4역할/동서남북/동일camera/중간피격나이의근접fixture.8장1920×1080직접검수/각전후fixturecore동일/원전체core복원/quiet. 머리·가슴기울임이보이며다리보행은유지. before가별도25bEXE라고표현하지않는다. 실제전체플레이나motionmovie증거는아니다.

profile-control01/after01는같은화염2800→3400tick·fixed60 CPUcallback대조용이며최종real-time성능과구분. 결과/실행상태를먼저확인하고중복실행하지않는다. 미연결연구로보존,채택전비용과실제연속동작추가판단필요. core와현재25bfreeze불변.

CPU-COMPARISON01.json: 각1회동일화염2800→3400tick/정상core독립동일/quiet.25b대26 배우callback평균1.831893→1.908292ms/최대4.207→4.266ms. process최대28.810→28.111ms/physics최대2.876→2.947ms. 양쪽224생성/112checkout;26에서44hitblend. 이구간의부가비용은작았으나후반고밀도/모든환경/제품formal승인자료가아니다. 두실행terminal,중복하지않는다.
