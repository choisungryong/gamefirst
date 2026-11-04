## 저장23 보존 경로 복구 · 2026-11-04

이번 보존 감사에서 기본 Quality23 디렉터리가 없어 책 생성01이 중단됐다. 현재 없어진 원인은 확인되지 않았다. full23/runtime/default-reload01/profile-after.json 및 profile-before.json에 기존 pins의 두 해시와 정확히 같은 바이트가 있어, 존재하지 않는 원래 디렉터리에 profile+revision1+revision2 세 파일을 xb 모드로 복원했다. 기존파일 덮어쓰기·사용자29변경 없음. save23-recovery01/BEFORE.json과RESULT.json에 사전부재·원본사본·해시·복원완료 보존. 현재3개해시모두원pin같음. '계속존재했음/아무변화없음'으로해석하지말고, 발견된부재와바이트동일복구를구분한다. 별도 책 생성02 완료. 제품29와 새 시안 소스는 불변이다.

# 군중 체형30 연구 · 제품29 유지

chapter_actors_quality30/30b/30c.gd는 모두 제품 미연결이다. 30은 역할별4가지 몸 전체 비율,30b는 같은4체형의 머리/어깨/팔 비율을 더한다.30c는30b와 동일 표현을 유지하면서 뼈 인덱스와 checkout당 base array를 재사용한다. 원래29의 피격·paid회복방향·그림자·pool224/공유skin1 유지. ID/generation으로 시각변형만 선택,simulation RNG/충돌/공격/획득/성장/새 geometry 없음. 정예와 최종보스 형상 미변경.

compare01/session88103와 compare02/session92224 모두 import/check/GPU exit0-stderr0. 정상냉기2800/12600/19800tick(46.7/210/330sim초) 같은core·camera·light·pose에서 off/on,각6PNG. 모든출력core같음/생성224/skin1. compare01은12600전후2장 직접봤고 차이약해미채택. compare02는6장전부직접검수,목·어깨·팔과몸비율차이로외곽개체반복이조금줄지만같은모델계열한계와밀집중앙중첩은남음. 별도몬스터종을추가한것처럼쓰지않는다. rawpixel차이수는품질점수가아님.

fixture01/session22348 headless11검사quietpass:정상군중12role/variant전부·반복자세누적없음·modal정지·손/지팡이·hit28·원core·풀224복구·키/alias·bonebase초기화·skin1.30b범위.

mapped01/session95266 두팔29/30b 각300PNG 및60fps normal2초/공격fixture3초MP4. 정상16001~16120 모든frame/tick/coreSHA같음/전체정상core복원/quiet/8검사pass. 공격fixture는4역할각한cardinal방향뿐이며모든variant/방향연속영상승인아님. 직접본6장:29예고20/회복70,30b예고20/타격48/회복70/정상60. paid방향과역할윤곽유지확인. 전체MP4직접재생·청취승인아님. 무음offline정상재생속도자료/실시간성능또는수동증거아님.

cost01/session19442 실제source1920×1080/VSyncoff/uncapped/ignorefocus/정상화염2800checkpoint/2초warmup+10초OS시계각1회:29 p50 3.810/p95 5.913/p99 6.814/max35.330ms→30b 5.067/7.572/8.637/35.551ms. cost02/session66459 같은방식새비교:29 3.854/6.080/6.797/34.326→30c 4.815/6.952/7.900/39.797ms.각pair독립core같음/양쪽>33.33각1/drawmax300동일/quiet/각pair끝3528·3529로1tick차이.30c비용추가여전히있음.서로다른pair의차이를정밀개선율로쓰지않는다. 실제focus패키지대표3회나전체후반보증아님.

equivalence01/session2554 정상60step(2800→2860)배우5979개표본의모든bone/modelscale/staff30b=30c/modal/pool같음/6검사quietpass. 확장equivalence02/session84003는그8검사모두true에도ObjectDB종료경고stderr124로실패. stage/result/raw/FAILED-RESULT/FAILURE를그대로보존/동일출력재실행없음. extra control presenter와view를명시해제한새equivalence03/session7176 --verbose는같은8검사·5979normal+8640공격표본전부일치/exit0-stderr0. 3역할×4체형×4cardinal방향48체,180fixtureframe의windup→paid회복→modal→hit→death를비교했다. 결과scope상속문구는60normal만쓰지만attack_comparisons8640와checks가확장범위를명시한다. 이것은30c가30b표현과같다는headless근거이지사망/공격예술품질승인아님. 첫경고의정확한내부누수객체원인은확정하지않는다.

현재모든이번Godot프로세스종료직접확인. 제품29 rootfreeze/모든새stage/사용자23저장3/사용자29최신rev2저장+journal불변(PRESERVATION02).기존후보14~29·실패·도감v29이하보존.30EXE없음. 제품채택전에추가비용대비화면가치판단과실제30c패키지검수가필요하다. 다음은30c의bodyvariation을과장하지않고기존29보존하에채택여부결정/필요시새30패키지와actualGPU검수다. 공간구조깊이와최종수동전체·실청취는여전히남음. 목표active/2·3장미착수.
