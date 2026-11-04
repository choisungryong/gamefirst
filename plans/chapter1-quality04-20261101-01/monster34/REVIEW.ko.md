# 해골 실루엣34 · 제품33 미연결 연구

이전원본 SkeletonOutlaw CC0 KevDev(source.html/SOURCE.json/원ZIP)의정확한conversion02사본을v01에보존했다. UI커널경로문제와무관하게원목표의다른몬스터몸/저작동작을검토한다. 스프라이트도구개발재개가아니라한게임에셋의준비다.

motion01 새고유stage에서import/check/headless샘플모두exit0-stderr0. 원GLB를재변환하거나기존GPUpreview03을중복재실행하지않았다. 65bone/9clip×300samples(60Hz)에서6marker월드좌표와전체bone회전기록. 분석결과원4.966초clip내반복:walk/run56frame(.933초),attack_slam68(1.133초),fan60(1초),cross72(1.2초),hit46(.767초). 자동반복최솟값후보이므로최종저작타격시점/시각승인으로쓰지않는다. 첫slam손속도peak.417초근처. death1.68초와3.35초에리셋점이보여첫회무너짐후hold필요. 실제게임판정시점은코어그대로표시기에서맞춘다.

merge01:원8mesh/6skin(각57bind)을공통bind공간으로변환하여1mesh/2surface/1skin의v02를생성. 소스joint목록같음확인/각skin의공통변환수학검증/가중치0이아닌모든vertex-influence의bind등가오차최대2.87971e-9(원bind공간).6594삼각형·UV·원jointweights(몸통8weights포함)·9클립curve·두embeddedimage그대로. 같은image를쓰는몸재질은metal.03/roughness.79,도끼metal.1로정리하였으므로원화면픽셀동일주장금지. sourcev01절대덮어쓰기없음.

motion02는새v02만import/check/headless샘플,모두exit0-stderr0. 보존motion01결과와비교해2700sample의6marker좌표·65bone회전·clip길이전부exact같음,실제엔진1mesh/2surface확인. 원source GPUbaseline중복실행안함. 새v02 GPU화면/게임play/adoption/성능승인아님.

현재제품33/Core16/World31d/Actor32b/FX33b와원freeze/기존EXEs/사용자23복원후·29rev2는PRESERVATION01모두pass. 모든이번headlessprocess종료/GPU새실행없음. 기존preview03 PNG3장을앞턴에서직접봤지만v02신규GPU검수로승격하지않는다.

다음:미연결Actor34 표시기에서walker에새몸을연결하고나머지역할/보스유지. 기존Mophs Spine1/Hand.R와새ORG-spine/ORG-hand_R의뼈이름·인덱스가다르므로Actor28/30/32뼈캐시를그대로대입금지. super.setup의기존pool로캐시를만든뒤walker모델교체하거나분리표시기로명시연결. 풀224/모달·빙결·냉기사체·피격상체·가림·paid공격방향·보행거리연결·현재성장/저장/공격판정유지. 첫공격1주기와사망리셋전hold를실제화면에서검수해야함. 아직Actor34소스/34EXE/게임stage없음. 원목표active/추가툴·Github보류. UI연결복구질문답대기,수동/청취/최종focused성능미완료.
