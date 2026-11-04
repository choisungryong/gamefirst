# 스프라이트 파이프라인 첫 구현 · 실제 브라우저→Godot 연결

제품은30 그대로다. tools/sprite_pipeline/compile.py·index.html·workbench.css/js·README.ko.md와chapter1/presentation/sprite_asset_presenter.gd를추가했다. 새표시기는제품30closure밖이며기존3D를대체하지않는다. 소스형식은기존가변region/feet/duration/ppm을보존하는legacy변환과4방향uniformgrid등록spec. PNG와manifest/actor.json을새출력으로등록하고원본·기존출력덮어쓰기를거부한다. PNG슬롯·방향·발기준·시간연결이며정지이미지의없는포즈를생성하지않는다.

COMPILER-RESULT.json 22검사pass:보존5역할legacy의모든region/feet/PNG바이트같음,누락방향·범위밖frame·0duration·범위밖rect는출력전거부,기존출력덮어쓰기거부,root30freeze불변. 실제uniformgridfixture는원walker16frame을발기준으로재배치한test PNG일뿐신규productionart아님. GRID-COMPILE.json 실제specCLI통과.

engine01/session98087 headless/check/GPU 모두exit0-stderr0. sameGodotpresenter에5역할등록을읽혀모든authoredclipframe·사망마지막hold·누락동작명시fallback20검사pass,실제1280×720 PNG5캐릭터화면직접검수. 현재3D게임의스프라이트교체나전투검수아님.

실제IAB작업대에서PNGfilechooser→잘못된7행거부→4행과4이동방향연결→16frame/누락3action안내→등록JSON다운로드확인. C:/Users/twins/Downloads/grid-walker-browser.sprite.json을원PNG와새browser-export01로사본보존후그대로CLI컴파일. engine02/session71513가그실제브라우저출력을Godot에서읽어4방향16frame정확샘플/누락death명시대체pass,headless/GPUquiet. 기존출력덮어쓰기없음. 소스선택표시가예제hero로남던UI문제는이전JS사본browser01에보존하고새PNG이름으로표시수정/재검수. 비동기예제로드역전도ticket으로방지.

도감full30/book-v31/dist/workbench/index.html,전체42HTML/1813refs/missing0. rootindex와candidate30,workbench×1440/390폭6case만신규browser검수 main=h1=1/overflow0/완료broken0/pending0/viewportreset/screenshot직접검수/markDeliverable. 기존v30이하보존. 작업대의예제선택·한frame·방향·death재생→frame4/4정지·실제PNG등록·오류·export를검수했다. 전체책새검수아님.

PRESERVATION-AND-PRODUCT30-AUDIT01은원30runtimefreeze/원stage/원EXE/이전EXEs/사용자23복원후3와29최신rev2+journal/두pipeline단계stage·실행결과모두pass.30초반observer실패는그대로실패.30전체/수동/실청취/formal3회·최종질감미완료. 원시기술통과로목표완료취급금지.

남은파이프라인작업:등록된asset을기존역할의presenter슬롯에선택연결하는레지스트리와실제전투미리보기. 현재작업대는PNG등록→미리보기→설정export→CLI등록→공용Godot표시까지이며UI한번으로현재게임을자동교체한다고쓰지않는다. core공격타이밍/피해는그대로유지한다. 이후같은몹추가마다전체장검사를반복하지말고변경범위에맞춰asset검수/출시후보묶음검수. 원1장목표active/2·3장미착수.
