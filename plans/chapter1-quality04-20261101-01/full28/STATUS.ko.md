# 현재 제품28 · 2026-11-04

EXE SHA a925cb49aa7fc1c0e99e6ddc5e44166394e7d700084f6eb5f4b9e77d0bd2115d/130065656bytes/runtime125-stage127-PCK227. Core16/World22/Actor28/HUD27/Input21/FX26. root main/preset Baseline 유지,패키지Quality28별도저장. 기존27이하 EXE/stage/소스·실패·기본23저장+journals3파일 보존. 원27assembly/rootfreeze는 C:/Project/game-research/implementation-backups/chapter1-before28-20261104-01 에 보존했다.

Actor28은 .2초 상체9bone의 기존hit클립 최대.85혼합과Spine1최대.238rad반동을 추가하고,회복 동안 이동방향 대신paid attack_direction을 유지한다. 다리로컬포즈·core좌표·피해·공격시간·이동규칙불변. 공격/죽음/빙결·modal이 피격보다 우선하며지팡이손추적/풀재사용초기화 유지. World27바닥은 미채택.

actor28/fixture02 47항목quietpass. CPU대조각1회평균배우1.871573→1.960958ms,추가.089386ms/최대4.075→4.261ms/동일core. 최종성능아님. 이전sample영상과MovieMaker동기분석실패자료는보존.

mapped01은fixture enemy_attack 이벤트kind누락으로25b실행stderr2048/runner실패,300PNG와결과/log보존,28팔미실행. 제품버그로간주하지않고helper보완mapped02 새stage에서수행. mapped02 session78926 두팔quiet/각300연속PNG(정상120+복제공격180),모든프레임phase/index/tick/coreSHA같음,정상틱16001→16120/원core복원.각PNG직접60fps인코딩으로시작/정리프레임제외. 회복70frame에서기존4역할모두paid와약90도차이/새표시오차1e-7rad이하,예고20frame은양쪽paid유지. 각역할하나씩서로다른방향인fixture이며모든역할×모든방향을다검증한주장은아님. 직접검수:구회복70/신예고20·타격48·회복70·정상60 총5장. 전체MP4직접재생검수는별개다.

패키지import/export/PCK/30sim초headless/releasebehavior quietpass. 실제hit01 session80443/PID28260 terminal exit0-stderr0:정상획득2800tick체크포인트후원래live정책/controller로3400tick,48표시혼합/224생성112재사용/독립전체core같음/실제1920×1080/HUD27·FX26·Actor28로딩확인/profileoff. afterPNG직접검수. 실제EXE부분live증거이며manual/fullchapter/hearing/formal성능아님.

independent-audit01 38항목모두pass. 기존14~28stage/모든이전EXE(실패25포함)/기본23저장3/원27assembly/새freeze/검수Actorexact/47검사/mappedcore·4방향회복/30초core10상태같음/실제hit·로드·quiet·1080p·pool/PCK재파싱 포함. mapped01 session3467 실패종료/패키지17116 성공종료/actual80443 성공종료,중복실행금지.

최신도감book-v27 생성/브라우저검수는해당BUILD/BROWSER기록을따른다. 남은실질과제는 공간 깊이의구조·조명개선,최종정상속도수동전체·실청취·동일최종EXE대표성능3회/전체후반리듬. source검사·부분GPU·과거다른후보의성공을최종품질완성으로간주하지않는다. 같은수동입력도구왕복지연실패방식반복금지,목표active/2·3장미착수.
