# Actor25 일반 적 표시 재사용 연구 · 2026-11-03

원25 미연결 source는 보존. profile01은 전체core동일/quiet/재사용44회이나 actor최장57.993ms로24의56.919ms 대비 개선 입증 없음. fixture01은11개수명검사quiet. 원시 자료를 덮어쓰지 않았다.

별도 chapter_actors_quality25_warm.gd는메뉴전에 walker144/ranged40/charger40 총224개를준비한다. core에가짜적을추가하지않고 hidden disabled SceneTree 부모에 표시노드만보관한다. core에서사라진일반적만종류별재사용하며retained corpse/elite/finalboss는원수명유지. reset시재질alpha/tint·포즈·metadata/motion/entitykey를초기화한다.

warm-profile01 정상2800→3400tick fixed60 계측은전체core동일/quiet/누적224생성·174checkout. 관측78번 _create 최대150us/배우callback최대9.137ms/process41.823ms. 기존24 profile02 actor56.919ms/단일생성16.452ms. callback비교이며실시간FPS수치가아니다. warm-fixture01 11개와warm-fixture02 50개 모두quiet. 후자는실제공격·빙결·modal·찬사체·boss예외·mesh배열·독립rig/material·반복reset 포함. warm-replay01 정상16000→16600tick전체core동일/quiet,4실제PNG1920×1080직접검수: 냉기파쇄/사체/역할색·지팡이/돌진과입력안내유지. 부분재생,수동/전체아님.

source-performance/trial01은외부stage의source상대경로evidence guard가repo경로를거절해측정전종료. runner는없는probe복사에서실패. nativeexitcode미저장/PID28368없음확인. 원본helper복사와raw유지.02는source전용절대evidence base를지정한별도probe clone을썼고기존probe/package는불변.

같은Godot엔진/같은frozen stage/정상냉기90131/pilot/실제메뉴클릭/focus활성/VSync off/uncapped/MSAA2/Forward+/time_scale1/10초warmup+60초OSmonotonic/sample중이미지와I/O없음/전후실제1920×1080계약의각1회순차대조: control01 Actor24 vs trial02 warm25. 둘다valid/quiet. p95 11.096→11.242ms,p99 16.773→15.171ms,최장71.939→60.527ms,16.67초과126→55개,33.33초과56→6개. 정적메모리끝값140635166→160890822bytes. MATCHED-COMPARISON01.json에원시최장행/감사보존. 한쌍순차source검사이지무작위반복/실제제품/최종3회승인이아니다. 기존candidate24 release formal01과source수치를혼합하지않는다.

startup01은동일import stage에서headless표시setup각1회순차:24 setup331972us/memorydelta119846029bytes, warm setup1021459us/memorydelta143449989bytes. 추가약.69초/23.6MB. 모델/영웅setup포함,차가운실행전체/첫메뉴/GPU컴파일/프로세스working set증거아님.

이근거로full25별도개발후보채택/기존24백업.제품실제화면·대표성능·수동전체·실청취·최종미술품질은별도검수한다. core16/World22/FX22/HUD23/Input21유지. 이전후보/성공실패/사용자저장보존.
