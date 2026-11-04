# 해골 실루엣34 · 제품33 미연결 연구

이전원본 SkeletonOutlaw CC0 KevDev(source.html/SOURCE.json/원ZIP)의정확한conversion02사본을v01에보존했다. UI커널경로문제와무관하게원목표의다른몬스터몸/저작동작을검토한다. 스프라이트도구개발재개가아니라한게임에셋의준비다.

motion01 새고유stage에서import/check/headless샘플모두exit0-stderr0. 원GLB를재변환하거나기존GPUpreview03을중복재실행하지않았다. 65bone/9clip×300samples(60Hz)에서6marker월드좌표와전체bone회전기록. 분석결과원4.966초clip내반복:walk/run56frame(.933초),attack_slam68(1.133초),fan60(1초),cross72(1.2초),hit46(.767초). 자동반복최솟값후보이므로최종저작타격시점/시각승인으로쓰지않는다. 첫slam손속도peak.417초근처. death1.68초와3.35초에리셋점이보여첫회무너짐후hold필요. 실제게임판정시점은코어그대로표시기에서맞춘다.

merge01:원8mesh/6skin(각57bind)을공통bind공간으로변환하여1mesh/2surface/1skin의v02를생성. 소스joint목록같음확인/각skin의공통변환수학검증/가중치0이아닌모든vertex-influence의bind등가오차최대2.87971e-9(원bind공간).6594삼각형·UV·원jointweights(몸통8weights포함)·9클립curve·두embeddedimage그대로. 같은image를쓰는몸재질은metal.03/roughness.79,도끼metal.1로정리하였으므로원화면픽셀동일주장금지. sourcev01절대덮어쓰기없음.

motion02는새v02만import/check/headless샘플,모두exit0-stderr0. 보존motion01결과와비교해2700sample의6marker좌표·65bone회전·clip길이전부exact같음,실제엔진1mesh/2surface확인. 원source GPUbaseline중복실행안함. 새v02 GPU화면/게임play/adoption/성능승인아님.

현재제품33/Core16/World31d/Actor32b/FX33b와원freeze/기존EXEs/사용자23복원후·29rev2는PRESERVATION01모두pass. 모든이번headlessprocess종료/GPU새실행없음. 기존preview03 PNG3장을앞턴에서직접봤지만v02신규GPU검수로승격하지않는다.

다음:미연결Actor34 표시기에서walker에새몸을연결하고나머지역할/보스유지. 기존Mophs Spine1/Hand.R와새ORG-spine/ORG-hand_R의뼈이름·인덱스가다르므로Actor28/30/32뼈캐시를그대로대입금지. super.setup의기존pool로캐시를만든뒤walker모델교체하거나분리표시기로명시연결. 풀224/모달·빙결·냉기사체·피격상체·가림·paid공격방향·보행거리연결·현재성장/저장/공격판정유지. 첫공격1주기와사망리셋전hold를실제화면에서검수해야함. 아직Actor34소스/34EXE/게임stage없음. 원목표active/추가툴·Github보류. UI연결복구질문답대기,수동/청취/최종focused성능미완료.

## 일반 근접 연결34/34b · 2026-11-05

Actor34는Actor32b상속,super.setup에서기존Mophs28/30/32캐시를만든뒤poolwalker144의모델만해골v02로교체한다. root/코어AI/판정/공격시점/드롭/성장/저장불변. 나머지3역할과보스유지. 새65bone에Mophs인덱스를대입하지않고ORG이름의자체상체hit13샘플과가림spine/head/도끼swing을사용한다. 원clip의첫56frame보행·첫68frame공격/paid0.417초정렬·사망1.6초hold. 새몸바디비율.60~.645/head.72. author연출을기존corewindup/recover길이에매핑하며원root/hurtbox옮기지않는다.

mapped01/session67696는관찰기들여쓰기오류로check exit1-stderr244. GPU양쪽미시작,원시/FAILURE/source그대로. 관찰기수정한mapped02/session10905는32bquiet/34 GPU exit0이나material-nullRD stderr571로strict실패. 정상core/300framecore같음과별개로실패보존. 첫34의normal60/attack20두장만직접검수. 기존모델제거때meshbase를분리하지않은해제순서를의심하지만내부원인확정금지.

34b는이전모델제거전각MeshInstance.mesh=null로렌더base연결을먼저분리한다. boot01/session53772 짧은20renderframe+cleanup진단은import/check/GPUexit0-stderr0. boot초기manifest계산뒤GLB를복사한누락은source-asset-addendum.json에투명하게기록,초기manifest덮어쓰기없음.

mapped03/session41423는새34b만검수,보존mapped02/32b baseline결과재사용(GPU중복실행없음).import/check/check-actor/34bGPU/encoding모두exit0-stderr0.120정상step+180copiedattackfixture각300row의매frame/tick/corehash같음/원정상core복원/새와기존family공존/144walker교체/10checks pass. 새34b300PNG/무음60fps normal2초·attack3초영상보존. 직접검수5장:기존32bnormal60/34bnormal60/34battack20·48·70. 해골·도끼윤곽과기존원거리/돌진형상이구분되고공격전후도끼위치변화읽힘. 전체영상직접재생·모든방향검수·실시간성능·수동·패키지34승인아님.

regression01 headlesscheck/run exit0-stderr0/16checks pass. 실제정상2800snapshot에서가역fixture로65bone/재질2/20회반복누적없음/head.72/정지·빙결posehold/피격상체만변함/첫주기windup-recover/paid방향/사망반복전hold/풀224복구·family재checkout·alias없음/전체정상core복원확인. 같은mapped03stage핀불변,외부fixture소스해시input.json기록.

cost01/session24248 현재실행중:full33동일World/FX/기준Actor32b vs34b,정상화염16000체크포인트/2초warmup+10초OS시계비교. launch/execution/raw/process로종료확인전재실행금지. 제품33은그대로/34EXE없음. 다음은비용확인과새근접4방향·사망화면·실제패키지검수후채택판단. 기술pass만으로미술완성선언금지. 기존fail/source/모든후보/사용자23복원후·29rev2는PRESERVATION02보존확인. UI연결복구질문답대기/최종수동·실청취·최종focused성능남음.

## cost01 종료

session24248 양쪽GPU exit0-stderr0/COMPARISON완료. 정상화염16000checkpoint/2초warmup+10초OS시계각1회/실제1920×1080/uncapped/VSyncoff/ignorefocus/profileoff/측정중readback없음.32b→34b p9510.101→10.548ms,p9911.217→12.352,max12.769→13.950,33ms초과0/0,drawmax384→546. 시작16128/16129로1tick차이/끝둘다16729각독립전체core같음. draw추가비용있음/정식focused패키지3회대체금지.34b after1080PNG직접검수,뼈·도끼근접형과기존원거리·돌진형상구분/주인공표식·위험원·이름읽힘. 모든이번Godot종료/같은검사재실행금지. 다음은새walker4방향과사망화면및패키지검수.현재제품33유지/34EXE없음.
