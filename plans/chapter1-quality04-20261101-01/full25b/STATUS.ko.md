# 최신 재개 — 2026-11-04 / 25b 냉기 전체 GPU 완료·미연결 Actor26 피격 반응 / 도감v21

제품/root는25b고정. EXE SHA6a45fc58934e138eee0ab1a976f5ce44a60c2d67626df7b5656a8f36356f3d98/runtime122-stage124-PCK221/core16/World22/FX22/HUD23/Input21/Actor25b. 먼저full25b/runtime/WHOLE-COLD-REVIEW.ko.md와hit26/REVIEW.ko.md를읽는다.26은미연결source이며26EXE없음. 기존14·16·17·17b·18·19·20·21·22·23·24·실패25·25b,모든source/성공실패/사용자저장보존. root25bfreeze/과거EXE와23기본profile+revision3파일핀을전체검사후재확인했다.

실제25bGPU gpu-cold01 완료:원normalpolicy/냉기90131/기본HP·획득/profile-off/ignore-focus/maxfps120/캡처포함. 최초승리23862tick=397.7sim초/3451킬/Lv12/34장비,기존16실제냉기전체10상태모두일치/파쇄840(냉기사망823)/quiet. 224노드추가생성없이3461재사용/끝pool198,30tick간격소유관계794표본모두정합/각zone기록. 모든frame검사나formal성능/수동/실청취승인아님.27PNG보존,중간210·후반270·보스사망후.35/.90/1.60초5장직접검수. 주변소거→보스붕괴→겨울의심장보상모달확인. sourceprofileoff실행이라저장0표시는의도된QA상태. 기본저장증거는23의실제기본user경로happy path범위로보존.

Actor26:기존hitclip상체9bone을.2초최대.55혼합/다리보행·공격예고·dash/recover·death우선/빙결·modal완전pose정지. 초기13pose캐시로추가player샘플링회피,전프레임base9pose복구로20Hzskip누적변형방지. rangedstaff혼합/복구후Hand.R에동기화,checkout임시metadata정리. 원fixture01 source는그stage보존. 보완후fixture02 43headless검사quiet/원core복원. GPUreplay01 정상화염16000→16600tick/648blend/전체core독립기준동일/quiet/4PNG직접검수. compare01 같은26혼합off/on·4역할·동서남북근접8PNG모두직접검수/fixture와원core복원/quiet. before는별도25bEXE가아니며실제motionmovie도아님. 반응강도작고최종타격감승인아님.

같은화염2800→3400tick fixed60 CPU각1회대조profile-control01/after01: actor평균1.831893→1.908292ms/최대4.207→4.266ms,양쪽전체core동일/quiet/224생성·112checkout,26에서44blend. 추가비용은작으나실시간formal/후반밀집/제품승인아님.26은아직채택하지않고연속동작·반응강도판단남음. 현재25b최종대표성능은이전formal01 1회뿐(p959.282/p9912.575/max56.330/>33.33 6). 새wholeGPU를대표성능으로바꾸지않는다.

최신도감full25b/book-v21/dist/index.html(실제IAB탭9는hit26.html).32HTML/1069refs/missing0,32×1440/390폭64case h1=1/overflow없음/broken0/viewportreset/실제screenshot확인/markDeliverable. v20이하보존. whole25b.html과hit26.html에서실제전체와미연결시안구분.

이번모든실행terminal:whole39319/PID29296 exit0,headless26fixture44656·38120성공,26replay준비27147(GPU미실행)뒤별도GPU57645성공,compare69828성공,CPUcontrol59760/after97046성공. 마지막프로세스조회게임없음. 동일검사재실행하지않는다. GPU중복없었고전체GPU중에는다른26검사는headless만실행했다.

다음구체품질문제: actual25b전체후반/보상그림에서바닥장비이름이너무작다. cloister_effects.gd:310의Label3D font26/pixel_size.0075/8m범위표시가원인. 제품25b유지한별도FX시안에서실제1080p글자크기/이름겹침/회수표시를개선하고표시대비·무조작수집/드롭규칙불변확인. Actor26연속동작강도판단도이어간다. 정상속도수동전체·실청취·최종제품1080p3회·중앙공간과군중전투/장비발견최종품질여전히미완료. 목표active/2·3장미착수.

---
# 최신 재개 — 2026-11-03 / 후보25b 릴리스·실제 GPU 첫 성능 확인 / 도감v20

현재 제품25b: builds/chapter1/chapter1-full-candidate-20261103-25b/AshenCloister-Chapter1.exe SHA6a45fc58934e138eee0ab1a976f5ce44a60c2d67626df7b5656a8f36356f3d98 /130056648bytes/runtime122-stage124-PCK221. core16/World22/FX22/HUD23/Input21/Actor25b. 먼저full25b/STATUS.ko.md,pool25/REVIEW.ko.md,full25/FAILURE.ko.md를읽는다. root25b freeze고정/main과preset Baseline유지/패키지Quality25b별도저장namespace/profile-off검사. 이전14·16·17·17b·18·19·20·21·22·23·24·실패25 전부보존.

Actor25b는메뉴전walker144/ranged40/charger40 총224개표시만준비하고core에서사라진일반적만종류별재사용. retained corpse/elite/finalboss원수명유지. 실제core규칙/획득/드롭변경없음. source원25재사용만으로는개선없음보존. warm개발시안50+11검사quiet/후반정상16000→16600tick전체core동일/4PNG검수. source대조각1회33.33ms초과56→6,p95 11.096→11.242/p99 16.773→15.171. 준비setup부분계측추가.69초/정적메모리약20–24MB. 전체메뉴스타트/working set증거아님.

실패25:assert(_stash25(actor)) 부작용이release에서생략돼224노드고아,import/export/PCK후30sim초종료누수. EXE/stage/freeze/raw전부보존.25b는stash를assert밖에서항상실행/실패시queue_free. fixed-fixture01의GPU50검사quiet/RESULT완료이나wrapper마지막root24freeze검사는이미root25채택후라실패. POSTFLIGHT.json이실제root25freeze와stage모든핀일치확인. 같은GPU재실행안함/실패원시유지.

25b import/export/PCK/30sim초headless/releaseprobe 성공/quiet. 실제EXE formal01 실제냉기메뉴클릭/normalpilot/focus/10초warmup+60초캡처없음/RTX2070SUPER/Forward+/MSAA2/VSync off/uncapped/time_scale1/delta smoothingoff.13978표본/60.000652초,p50 3.516/p95 9.282/p99 12.575/최장56.330ms.16.67초과8/33.33초과6개. 기존24한회85/55개와비교. actualreadback전후1920×1080/보고Texture2304×1296원시보존/valid/exit0-stderr0. 실제actor25b로드/224누적생성/399checkout/끝pool181 확인. postflight 실제화면검수. source수치와제품수치혼합금지. release static_memory_bytes0은미계측이지메모리0이아니다. 1회초반대표구간만이며최종3회/전체7분/수동전체/음향아님.

독립감사full25b/independent-audit01/RESULT.json 28항목pass:모든이전EXE(실패25포함)/14부터25b stage핀/기본23profile+revision3파일/새rootfreeze/실제테스트소스/PCK/30초core10상태일치/실제releasepool과quiet검증. 기본저장은23의실제기본user happy path증거를그범위로보존하며25b에서새로검증했다고말하지않음.

최신도감full25b/book-v20/dist/candidate25b.html.30HTML/936refs/missing0. 실제IAB탭8에서30×1440/390폭60case h1=1/overflow없음/brokenimage0/viewport reset/실제screenshot검수/markDeliverable. v19이하보존.

모든이번게임terminal:원25build10730 실패종료1/25bbuild15556성공/실제formal47564성공. source실시간trial01guard실패/PID없음,trial02 47058/control34594성공; GPUprofile3602/fixture59867·8328/replay26762/수정fixture37357터미널. 중복실행하지않는다. 새25b전체7분GPU는아직시작하지않음. 다음: 전체정상군중전투에서pool고갈/계속생성·zone전환/reset·boss보상까지수명확인,실제수동전체/실청취/중앙공간·공격실루엣·보상최종질감개선. 실제제품대표3회는아직1회뿐. 목표active/2·3장미착수.

---
