# C2 회랑 진입전 코어 계약

2026-10-31. `combat_run.gd`는 기존 Baseline/Expedition과 분리된60Hz 코어다. 마나 대신 기술별 쿨다운을 예약하는 독립 설계이며, 선택한 한 기술만 요청하는 이전 자동 시전과 달리 습득한 기술3개를 각자 예약·발사한다.70초에 정예 목표를 배치하고 실제 정예 처치 즉시 끝낸다.90초 시계만으로 승리하지 않는다. 이 구간은 첫 장 전체나 고유 장 보스 완료가 아니다.

## 공개 API

- `start(seed_:int=1, primary:String="chapter1.skill.ember")->bool`
- `step(move:Vector2=Vector2.ZERO)->void`: 호출1회=1tick. mode가playing일 때만 이동·쿨다운·AI·탄·XP가 진행된다. 입력 길이는1로 제한하고 비유한 벡터는0으로 처리한다.
- `elapsed()->float`, `alive_count()->int`, `get_next_dash_tick()->int`
- `get_offer()->Dictionary`, `choose(token:String,card_id:String)->bool`
- `open_inventory()->bool`, `close_inventory()->void`, `set_paused(value:bool)->void`
- `equip(uid:int)->bool`, `unequip(slot:String)->bool`, `compare_item(uid:int)->Dictionary`
- `effective_skill(id_:String)->Dictionary`, `snapshot()->Dictionary`
- `request_dash(direction:Vector2)->bool`:180tick 주기. 요청 후 진행하는1–12번째step에서 이동하고13번째부터 일반 이동으로 돌아간다. 요청 직후와 이후1–18번째step에서 피격을 무시하며19번째부터 피격된다. 일반 피격 뒤에는24tick 중복 피격 방지.

공개 상태를 표현자가 읽되 변경하지 않는다. snapshot/비교/효과 정의는 detached 사본이다. hero/enemies/projectiles/orbs/items/inventory/equipped/events는실시간표현용 읽기 계약이며 임의 외부 사전 변형에 대한 저장 입력 검증 API가 아니다. 저장/복원은 아직 구현하지 않았다.

## 상태와 사건

hero의 위치는Vector2(x,z), HP는1/256단위, 반경/속도는world meter 기준이다. enemies는단조 증가ID와런epoch generation을 쓴다. 개체를 재사용하지 않으며 사망 후75tick에 정리한다. spawn RNG·loot RNG·growth RNG는서로 분리한다. 최대활성180, 보유개체512, 탄384/적탄192, XP400, 바닥장비32, 일반소유64와정예보상전용1칸(소유합계상한65), 현재사건1024를상한으로쓴다. XP상한 도달 시기존orb에양을 합치며 보상량을 생성하지 않는다.

정예목표보상은바닥32칸과일반소유64칸의제한에막히지않고inventory에직접추가된다. 기존장비를교체하거나삭제하지않는다. item.objective_reward=true와snapshot.elite_reward_uid로구분하며현재inventory비교/장착API를그대로쓴다. 정상플레이의정예목표는1개이고중복처치/중복보상호출에도추가보상은없다. 일반드롭/회수는여전히64칸까지만허용한다. 런종료후inventory를열어65번째보상도장착할수있으며닫으면victory로돌아간다. 영구저장은아직없다.

mode는menu/playing/choice/inventory/paused/victory/defeat이다. 외부pause flag와inventory 상태를 분리해포커스상실 상태에서창을닫아도진행되지않는다. 성장선택이대기중이면inventory를닫은뒤choice로돌아간다.

events는playing step 시작에비우고선택/장착은append한다. 표현자는런마다seq를리셋하고사건의seq로중복소비를막는다. type/position/tick/seq가공통이다. cast/hit/death/xp_pickup/item_drop/item_pickup/equip/growth/level_choice/enemy_attack/hero_hit/dash/explosion/shatter/victory/defeat 등이있다. 사건 유실 상한은metrics.events_dropped로기록하며실제피해/보상은표현에의존하지않는다.

- cast: skill_id/direction/effects/targets/evolved. 효과는발사시점사본이다.
- hit: target_id/skill_id/damage_raw/frozen/shatter/radius_cm/blast_radius_cm/cast_uid/evolved. radius_cm은기술정의의의미를보존하며번개의경우연쇄탐색거리다. 실제폭발은별도explosion사건을쓴다.
- explosion: skill_id/radius_cm/cast_uid/evolved, death proc이면proc=true. 번개잔류폭발은3m로고정해7–9.5m연쇄탐색거리와분리했다.
- shatter: skill_id/radius_cm350/count/cast_uid/evolved. 현재는냉기피해로빙결대상을처치한경우의제한된파쇄다. 다른계열의마무리까지이어지는전체교차시너지라고표시하지않는다.

## 판정 경계

발사context는피해·형태·쿨다운값을고정한다. 이후장비/랭크변경으로이미발사한탄이강해지지않는다. 한시전의전역hit_budget과proc_depth≤1을소모한다. 번개는직접연쇄/분기/처치발동전체에서같은개체를1회만타격한다. 화염/냉기는서로다른탄의다중명중을허용하지만각탄의hit_ids와시전전역예산은유지한다. 사망/XP/드롭은사망전이1회에만발생한다.

위험 전조는AI발동거리가아닌실제플레이어중심위험영역이다. 근접circle1.15m=실제거리≤1.15, 정예circle3.4m=실제거리≤3.4. 돌진line은이동길이4.8m와반경.71m/폭1.42m의캡슐이다. 원거리fan은각ray방향과길이14.7m(정예17.5m),폭.88m를제공한다. 정예는circle/fan을번갈아사용한다. 빙결은남은windup/recover/dash시간을멈추어해제즉시보이지않는공격이발생하지않게한다.

맵은현재±19경계의열린공간이다. 실제벽충돌/내비게이션/개체간충돌은구현하지않았다. 표현자가중앙에막히는벽을배치하면안된다. 이동중적공간회피는추가검수영역이다.

## 검증

`test_combat_run.gd`:후보03은75행동검사actual0,의도적실패76검사actual1. 합성개체/XP를쓰는fixture이며정상플레이라고표시하지않는다. 선택정지·다중시전·장비형태·paid snapshot·무회복·보상1회·위험경계·빙결남은시간·냉기파쇄·번개중복/잔류범위·예산·실제정예종료·패배를확인한다. 추가경계는바닥32+소유0/63/64에서정예보상,기존UID/장착보존,보상중복방지,65번째보상비교/장착,일반회수64제한,대시12step/2.7m·13step정지·18step무적·19step피격·180step쿨다운이다. 이전후보02의52/53검사원본도보존했다.

`pilot_combat_run.gd`:HP/XP/장비/소환/킬을주입하지않고이동·회피·성장선택·획득한장비장착만입력한다.3주력×2seed를별도로기록했다.

- `evidence/core-pilot-20261031-01`:이전후보와소스사본보존.실제승리78.58–106.87초. 냉기1사례가90초를넘었다.
- `evidence/core-pilot-20261031-02`:번개잔류3m·안전한경계스폰·정예배치후보. 실제6/6승리75.70–88.12초,764–964처치,최대활성92–179. 모두실제정예처치로끝났고4장비슬롯을획득/장착했다. 후보02는01과배치/판정변경이있어한수치만으로개선원인을확정하지않는다.
- `evidence/core-pilot-20261031-03`:정예직접보상용1칸과대시경계수정후보. 기능75검사는통과했지만정상자동입력결과는5승1패(actual1,success=false)이다. 승리5개는75.13–88.85초,냉기seed71은64.9초/237처치/최대활성179에서실제패배했다. 대시1step증가로이동경로·회수·조우가달라지며이전6승을현재결과로인용하면안된다. HP/XP/seed/아이템을조정해실패를숨기지않았다. 냉기생존성/자동입력경로에검토과제가남아있으며C2균형·품질통과가아니다.

이는자동입력의코어실행이며실제사용자플레이·최종아트·음향청취·군중GPU성능·C2품질승인이아니다. 새로운통합실행본과실제화면검수는root가별도수행한다.
