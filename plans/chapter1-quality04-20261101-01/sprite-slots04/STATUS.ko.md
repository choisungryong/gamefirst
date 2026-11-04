# 역할 선택 파이프라인 · 전투 미리보기 연결 완료

제품30/rootfreeze/EXE659b264c6fe38929bfa4d35a08bd1c9b68b2d4e581a0e674d3e56284cb067863 그대로. tools/sprite_pipeline/roles.py·preview.py·combat_preview.gd와chapter1/presentation/sprite_asset_presenter_v2.gd·sprite_role_registry.gd·sprite_role_actors_preview.gd를추가했다. 모두현재제품closure밖의선택형미리보기다. 등록asset을기존hero/walker/ranged/charger/중간elite외형슬롯에연결한다. 미선택역할/최종boss는3D. core좌표/AI/능력치/공격/드롭/저장불변. 기존224pool상태에SpriteSlot자식을붙이고모델/지팡이를숨기는호환프로토타입이라3D리그CPU가남음/성능완성주장금지. V2는sharedAtlas와clipduration을캐시해샘플마다AtlasTexture를새로만들지않음. paidwindup은명시release앞부분,실제release/recover는그프레임이후로매핑.공격포즈/방향은원작화한계그대로.

slots01/session40324 첫headlesswalker는7기능true/core같음에도ObjectDBstderr124로실패,raw/RESULT/stage/FAILURE보존. 다른3arm미시작. slots02/session48967는새stageverbose진단headlesswalker만quiet,같은첫경고재현안됨/원인확정못함. cache명시해제추가한slots03/session6832는headlessallquiet. GPUwalker는exit0/기능7true지만verboseVulkan layer조회와RGB8변환warning stderr10433로strictgate실패(진단원문DIAGNOSTIC-WARNINGS).ObjectDB없음/첫경고가해결됐다고인과확정금지/GPUall미시작. 재실행으로raw덮어쓰지않음.

slots04/session30311은동일frozen03stage에서아직미실행이던GPUall만별도새output으로진행,exit0-stderr0/7검사pass. 두GPUcase정상냉기2800체크포인트→원래정책/controller3400tick/독립전체core같음. walker03은85walker만교체/다른역할3D;all04는hero+walker85/ranged5/charger12교체/fallback0/slotSamples68537.중간elite선택은레지스트리에포함되지만해당정상구간실제activeelite없음,실제중간elite전투검증으로확대금지. 최종boss는별도visual생성검사로3D유지확인/core엔티티spawn아님. 두afterPNG직접검수/실제1920×1080. sourcepreview이며EXE30/수동/whole/hearing/finalperformance증거아님.

roles.py는잘못된role/release누락/범위밖release3종출력전거부검사. preview.py는다운받은registry를읽어검증된manifest와asset만고유stage로복사/import/check/별도제1장실행한다.기존제품30baseline고정(향후새baseline전환시명시업데이트필요). 항상profileoff. sprite-preview-entry01/session57624 actualCLI headless/pilot/1초종료로import/check/preview exit0-stderr0,sourcepin불변. 명령사용법tools/sprite_pipeline/README.ko.md. 미리보기를닫으면종료하며,기존output덮어쓰기거부. 새몹마다전체장회귀검사를자동실행하지않는다.

도감v32작업대에서컴파일actor.json+PNG다중선택→등록객체표시→타격프레임빈값거부→이동전용gridasset의공격누락거부→완전walker예제불러오기→공격3/4프레임(0-base2)지정→C:/Users/twins/Downloads/walker-demo.roles.json실제다운로드확인. slots04/browser-export01에사본/해시보존,bindings가이미GPU검수한walkerregistry와exact같아서같은GPU재검사안함. 현재3D제품자동배포버튼아님.

최신full30/book-v32/dist/workbench/index.html 및sprite-roles.html,43HTML/1900refs/missing0. IAB2새탭 index+roles+workbench×1440/3906case만신규검수 main/h1각1/overflow0/completebroken0/indexdesktoplazy1·그외pending0. viewportreset/화면직접확인/markDeliverable. 기존v31이하보존. slots04/AUDIT01 현재30root/exe·이전EXEs·사용자23복원후3/29최신rev2+journals·01~04stage·실패원시·previewCLIstage모두pass.

다음은파이프라인최소연결을과장하지않고1장실제품질작업으로돌아간다. 방향별공격작화/가독성·스프라이트전용비용최적화는추가asset채택시범위맞게검수. 제품30의공간구조깊이·최종수동전체·실청취·최종동일제품성능/전체후반최종질감남음. 기존29성공을30승인으로확대금지. 같은긴도구입력왕복수동패배방식반복금지. 목표active/2·3장미착수.
