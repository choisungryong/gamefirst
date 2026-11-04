# 역할 선택 파이프라인 · 전투 미리보기 연결 완료

제품30/rootfreeze/EXE659b264c6fe38929bfa4d35a08bd1c9b68b2d4e581a0e674d3e56284cb067863 그대로. tools/sprite_pipeline/roles.py·preview.py·combat_preview.gd와chapter1/presentation/sprite_asset_presenter_v2.gd·sprite_role_registry.gd·sprite_role_actors_preview.gd를추가했다. 모두현재제품closure밖의선택형미리보기다. 등록asset을기존hero/walker/ranged/charger/중간elite외형슬롯에연결한다. 미선택역할/최종boss는3D. core좌표/AI/능력치/공격/드롭/저장불변. 기존224pool상태에SpriteSlot자식을붙이고모델/지팡이를숨기는호환프로토타입이라3D리그CPU가남음/성능완성주장금지. V2는sharedAtlas와clipduration을캐시해샘플마다AtlasTexture를새로만들지않음. paidwindup은명시release앞부분,실제release/recover는그프레임이후로매핑.공격포즈/방향은원작화한계그대로.

slots01/session40324 첫headlesswalker는7기능true/core같음에도ObjectDBstderr124로실패,raw/RESULT/stage/FAILURE보존. 다른3arm미시작. slots02/session48967는새stageverbose진단headlesswalker만quiet,같은첫경고재현안됨/원인확정못함. cache명시해제추가한slots03/session6832는headlessallquiet. GPUwalker는exit0/기능7true지만verboseVulkan layer조회와RGB8변환warning stderr10433로strictgate실패(진단원문DIAGNOSTIC-WARNINGS).ObjectDB없음/첫경고가해결됐다고인과확정금지/GPUall미시작. 재실행으로raw덮어쓰지않음.

slots04/session30311은동일frozen03stage에서아직미실행이던GPUall만별도새output으로진행,exit0-stderr0/7검사pass. 두GPUcase정상냉기2800체크포인트→원래정책/controller3400tick/독립전체core같음. walker03은85walker만교체/다른역할3D;all04는hero+walker85/ranged5/charger12교체/fallback0/slotSamples68537.중간elite선택은레지스트리에포함되지만해당정상구간실제activeelite없음,실제중간elite전투검증으로확대금지. 최종boss는별도visual생성검사로3D유지확인/core엔티티spawn아님. 두afterPNG직접검수/실제1920×1080. sourcepreview이며EXE30/수동/whole/hearing/finalperformance증거아님.

roles.py는잘못된role/release누락/범위밖release3종출력전거부검사. preview.py는다운받은registry를읽어검증된manifest와asset만고유stage로복사/import/check/별도제1장실행한다.기존제품30baseline고정(향후새baseline전환시명시업데이트필요). 항상profileoff. sprite-preview-entry01/session57624 actualCLI headless/pilot/1초종료로import/check/preview exit0-stderr0,sourcepin불변. 명령사용법tools/sprite_pipeline/README.ko.md. 미리보기를닫으면종료하며,기존output덮어쓰기거부. 새몹마다전체장회귀검사를자동실행하지않는다.

도감v32작업대에서컴파일actor.json+PNG다중선택→등록객체표시→타격프레임빈값거부→이동전용gridasset의공격누락거부→완전walker예제불러오기→공격3/4프레임(0-base2)지정→C:/Users/twins/Downloads/walker-demo.roles.json실제다운로드확인. slots04/browser-export01에사본/해시보존,bindings가이미GPU검수한walkerregistry와exact같아서같은GPU재검사안함. 현재3D제품자동배포버튼아님.

최신full30/book-v32/dist/workbench/index.html 및sprite-roles.html,43HTML/1900refs/missing0. IAB2새탭 index+roles+workbench×1440/3906case만신규검수 main/h1각1/overflow0/completebroken0/indexdesktoplazy1·그외pending0. viewportreset/화면직접확인/markDeliverable. 기존v31이하보존. slots04/AUDIT01 현재30root/exe·이전EXEs·사용자23복원후3/29최신rev2+journals·01~04stage·실패원시·previewCLIstage모두pass.

다음은파이프라인최소연결을과장하지않고1장실제품질작업으로돌아간다. 방향별공격작화/가독성·스프라이트전용비용최적화는추가asset채택시범위맞게검수. 제품30의공간구조깊이·최종수동전체·실청취·최종동일제품성능/전체후반최종질감남음. 기존29성공을30승인으로확대금지. 같은긴도구입력왕복수동패배방식반복금지. 목표active/2·3장미착수.

---
# 스프라이트 파이프라인 첫 구현 · 실제 브라우저→Godot 연결

제품은30 그대로다. tools/sprite_pipeline/compile.py·index.html·workbench.css/js·README.ko.md와chapter1/presentation/sprite_asset_presenter.gd를추가했다. 새표시기는제품30closure밖이며기존3D를대체하지않는다. 소스형식은기존가변region/feet/duration/ppm을보존하는legacy변환과4방향uniformgrid등록spec. PNG와manifest/actor.json을새출력으로등록하고원본·기존출력덮어쓰기를거부한다. PNG슬롯·방향·발기준·시간연결이며정지이미지의없는포즈를생성하지않는다.

COMPILER-RESULT.json 22검사pass:보존5역할legacy의모든region/feet/PNG바이트같음,누락방향·범위밖frame·0duration·범위밖rect는출력전거부,기존출력덮어쓰기거부,root30freeze불변. 실제uniformgridfixture는원walker16frame을발기준으로재배치한test PNG일뿐신규productionart아님. GRID-COMPILE.json 실제specCLI통과.

engine01/session98087 headless/check/GPU 모두exit0-stderr0. sameGodotpresenter에5역할등록을읽혀모든authoredclipframe·사망마지막hold·누락동작명시fallback20검사pass,실제1280×720 PNG5캐릭터화면직접검수. 현재3D게임의스프라이트교체나전투검수아님.

실제IAB작업대에서PNGfilechooser→잘못된7행거부→4행과4이동방향연결→16frame/누락3action안내→등록JSON다운로드확인. C:/Users/twins/Downloads/grid-walker-browser.sprite.json을원PNG와새browser-export01로사본보존후그대로CLI컴파일. engine02/session71513가그실제브라우저출력을Godot에서읽어4방향16frame정확샘플/누락death명시대체pass,headless/GPUquiet. 기존출력덮어쓰기없음. 소스선택표시가예제hero로남던UI문제는이전JS사본browser01에보존하고새PNG이름으로표시수정/재검수. 비동기예제로드역전도ticket으로방지.

도감full30/book-v31/dist/workbench/index.html,전체42HTML/1813refs/missing0. rootindex와candidate30,workbench×1440/390폭6case만신규browser검수 main=h1=1/overflow0/완료broken0/pending0/viewportreset/screenshot직접검수/markDeliverable. 기존v30이하보존. 작업대의예제선택·한frame·방향·death재생→frame4/4정지·실제PNG등록·오류·export를검수했다. 전체책새검수아님.

PRESERVATION-AND-PRODUCT30-AUDIT01은원30runtimefreeze/원stage/원EXE/이전EXEs/사용자23복원후3와29최신rev2+journal/두pipeline단계stage·실행결과모두pass.30초반observer실패는그대로실패.30전체/수동/실청취/formal3회·최종질감미완료. 원시기술통과로목표완료취급금지.

남은파이프라인작업:등록된asset을기존역할의presenter슬롯에선택연결하는레지스트리와실제전투미리보기. 현재작업대는PNG등록→미리보기→설정export→CLI등록→공용Godot표시까지이며UI한번으로현재게임을자동교체한다고쓰지않는다. core공격타이밍/피해는그대로유지한다. 이후같은몹추가마다전체장검사를반복하지말고변경범위에맞춰asset검수/출시후보묶음검수. 원1장목표active/2·3장미착수.

---
# 최신 재개 · 후보30 패키지/실제후반GPU 종료 · 스프라이트 파이프라인 착수

제품은 이제30이다. Core16/World22/Actor30c/HUD27/Input21/FX26. full30/build/build.json EXE SHA659b264c6fe38929bfa4d35a08bd1c9b68b2d4e581a0e674d3e56284cb067863/130070240bytes/runtime127-stage129-PCK231. root30freeze/backup C:/Project/game-research/implementation-backups/chapter1-before30-20261104-01 원29assembly/project/preset/freeze/23·29저장JSON보존. 기존14~29EXE핀/사용자23복구후3·29최신rev2+journals그대로. source30c는cost02검수본과exact같음. package session60169 terminal import/export/PCK/30sim초headless/releasebehaviorpass.

실제earlyfire silhouette01/session54419/PID4516 terminal exit1-stderr0:정상2800→3400tick/core전체같음/hit48/shadow224ON-OFF0/224생성112checkout/실제1920×1080/Actor30c로드. observer가짧은구간에12variant모두등장요구했으나실제11(ranged2없음)이라실패. FAIL/raw/proof그대로보존/성공승격금지. 실제afterPNG직접검수,발견카드·체형·회복방향읽힘.

별도newlatecold01/session75607/PID3752 terminal exit0-stderr0. 정상냉기획득19800checkpoint후원래livepolicy/controller20400tick/독립전체core같음/hit508/224생성95checkout/224shadowON-OFF0/실제1920×1080/Actor30c·HUD27·FX26/profileoff. 12rolevariants실제등장·유효범위/3role확인. afterPNG직접검수,보스위험원·냉기·드롭이름·배우외곽유지. 전체simchapter/수동/청취/formal성능아님. 이전29fullcold·formal3회는29범위그대로이며30의완료증거로대체하지않는다. 모든이번Godot종료직접확인.중복실행금지.

사용자가몹추가파이프라인과에셋북입력자동동작을질문했고,후보30안전정리후최소등록→미리보기→동작연결파이프라인을먼저구축하기로답했다. 이후3D와스프라이트동시지원방향. 기존정지1장으로없는동작생성하지않음/동작별시트입력의프레임·방향·발기준·타격시점메타데이터를자동연결하는최소도구착수. 제품30의3D를자동치환하거나기존스프라이트를덮어쓰지말것. 최종1장목표는그대로active/2·3장미착수.

---
