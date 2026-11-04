# 에셋북·1장 제작용 현재 자산/구현 사실

2026-10-31, Asia/Seoul. 사실 수집만 수행했다. 기존 제품·증거·사용자 저장·원작 파일을 변경하거나 복사하지 않았다. 최종 품질 판정과 설계 채택은 이 문서의 범위가 아니다.

## 조사 범위와 근거

직접 읽은 원문: `assets/licenses/{adventurers,skeletons,dungeon}-LICENSE.txt`; `tools/phase7_asset_ledger.py`; `tools/generate_phase7_audio.py`; `tools/generate_phase7_ambience.py`; `tools/build_phase7.py` 일부/포함·제외 목록; `data/README.ko.md`; `game_data/{catalog,equipment,loot}.json`; `data/{equipment_inventory,equipment_catalog,loot_catalog,progression}.gd`; `baseline_sim.gd` 관련 함수; `expedition_view.gd` 1–170; `presentation/{actor_registry,expedition_world,expedition_effects,expedition_audio,expedition_loot,expedition_hud,equipment_presenter,input_controller}.gd`; `plans/chapter1-replan-20261030-01/DOCUMENTATION-DISCOVERY.ko.md`.

GLB의 JSON 청크를 읽어 두 캐릭터의 animations/meshes/skins 목록을 확인했다. 파일을 실행·변환하지 않았다. WAV 헤더를 읽어 형식/길이를 확인했지만 실제 청취하지 않았다. 기존 Godot 공식 문서 목록은 위 발견 문서를 읽은 간접 확인이며 이 조사에서 웹 문서를 새로 열지는 않았다.

## 항목별 실제 보유 상태

| 에셋북 항목 | 실제 파일/구현 | 현재 확인된 범위 | 아직 확보·구현됐다고 할 수 없는 것 |
|---|---|---|---|
| 플레이어 | `assets/actors/Mage.glb`, `Mage_mage_texture.png` | KayKit Adventurers 모델. GLB에 1skin·12mesh. Idle/Walking_A/Running_A/Spellcast_Shoot/Spellcast_Raise/Spellcast_Long/Hit_A/Death_A/Dodge_* 등 클립 존재 | 최종 다크 판타지 캐릭터 조형·재질·의상·선택 화면·게임 카메라 품질 승인. 클립 존재는 회피 기능 구현의 증거가 아님 |
| 일반 적 | `assets/actors/Skeleton_Minion.glb`, 관련 texture | KayKit Skeletons 모델. 1skin·9mesh. 이동/근접/피격/사망/생성/부활/시전 등 다수 클립 존재 | 일반 적3역할에 맞는 서로 다른 최종 모델·실루엣·AI·원거리 탄·돌진 전조 |
| 정예 | `presentation/expedition_world.gd:110–132,142–168`, controller:179–185 | 같은 해골 모델에 스케일/색/4개 첨탑/링·이름·체력바 표현. 실제 개체 HP54로 변경 | 독립 정예 모델·고유 공격 패턴. 색/HP 변경을 새로운 AI로 표시 불가 |
| 보스 | 독립 보스 asset/handler를 읽은 범위에서 찾지 못함 | 기존 원정은 정예 처치+시간 조건으로 종료 | 고유 보스 모델·리그·공격/단계전환·전조·보상 연출 |
| 환경 | `assets/environment/{floor_tile_large,floor_dirt_large_rocky,column,wall_broken,torch_lit}.gltf.glb`, 각 texture | KayKit Dungeon5종. 21×21 반복 타일, 주변 기둥/벽, 횃불4, 프로시저럴 바닥 문양. `expedition_world.gd:2`는 소품이 장식임을 명시 | 연결3구역 맵·충돌/길찾기·실제 통행 가능한 구조물·최종 재질·소품 다양성 |
| 카메라/빛 | `presentation/expedition_world.gd:23–42,103–108` | Filmic, 안개, DirectionalLight3D, 정사영 Camera3D.size22/위치(12,18,15) | 최종 프레이밍 승인·타격 흔들림/섬광 설정·실제 최종 아트 아래 위험 가독성 |
| 화염/냉기/번개VFX | `presentation/expedition_effects.gd:19–39,57–100,104–140` | SphereMesh/TorusMesh/CylinderMesh와 색 재질. 명중 burst·원형파동·연쇄 두 segment. transient160/projectile128 상한 | 제작된 입자 텍스처/flipbook·독자 shader·화염 궤적·빙결/파쇄·다단 성장/진화별 효과 묶음 |
| 전투 음향 | `assets/expedition/audio/{fire,cold,lightning,impact,hurt,death,drop,pickup,equip}.wav` | 자체 합성 cue9개. 전부22,050Hz mono16bit. 길이 약0.13–0.60초. 생성원문/CC0 프로젝트 헌정 명시 | 최종 sound design·레이어·재질별 명중·변주·실제 군중 믹스 청취 승인 |
| 배경음/음악 | `assets/expedition/audio/ambience.wav` | 자체 합성4초 바람 loop,22,050Hz mono16bit | 작곡된 전투/Boss 음악·단계 전환·긴 ambience 라이브러리 |
| HUD/UI | `presentation/expedition_hud.gd:46–158`, `equipment_presenter.gd:125–159` | Godot Label/Button/Panel/StyleBoxFlat로 구성. 체력/마나/XP/기술버튼/정지·시작·승패/장비 모달. 장비는 이름·조건·modifier 문자열과 장착 버튼 | 최종 아이콘/품질 프레임/기술 카드/진화 트리/장비 나란히 비교/에셋 스타일 원장 |
| 드롭 외형 | `presentation/expedition_loot.gd:11–65` | PrismMesh1종, common/crafted 재질2개, UID+epoch별 이름표·겹침 회피. 최대32marker | 장비별 ground mesh/아이콘·여러 품질의 드롭 연출·필터 UI·핵심 고유효과 표현 |
| 장비 데이터 | `game_data/equipment.json:7–15` | base3종: 불씨 지팡이/focus, 수호의 로브/body, 샘의 부적/charm. affix3종. 요구Lv1/1/2 | 계획의4슬롯·base12·affix12·고유효과3은 미구현 |
| 성장 | `data/progression.gd:1–13` | 처치당XP3, XP6→Lv2·18→Lv3. 장비 요구 조건 해금만 수행 | XP회수 오브·3지선다·런 skill rank/패시브·스킬진화·성장곡선 |

## 라이선스·출처를 에셋북에 적을 수 있는 사실

세 KayKit 원문 모두 저자/배포자 Kay Lousberg, 라이선스 Creative Commons Zero(CC0), 개인·교육·상업 사용 허용, 크레딧 비필수라고 적혀 있다. 각 원문을 별도 보존하므로 단순히 ‘무료’로만 기록하지 않고 source/license 파일을 연결할 수 있다.

- Adventurers Character Pack1.0, 원문 creation date13/03/2023.
- Skeletons1.0, creation date02/02/2024.
- Dungeon Remastered1.0, creation date13/03/2023.
- 자체 WAV 생성기 두 파일은 외부 샘플을 쓰지 않는 합성/CC0 헌정을 명시한다. 소리 품질이 승인됐다는 뜻은 아니다.
- `tools/phase7_asset_ledger.py:12–42`는 source/license/SHA/usage/WAV 형식과 원작 연구 자산 분리를 기록한 기존 패턴이다. **고정 출력 경로가 이미 있는 보존 파일이므로 그대로 다시 실행하지 않는다.**
- `assets/firebolt-sheet.png`, `assets/firebolt-decoded.json`, `assets/reference/original-cast-strip.png`는 연구/비교 자산이다. `baseline_view.gd:76,422`는 이를 참조한다. 최종 에셋으로 사용할 수 있다는 근거가 아니다.
- 원정 배포는 `tools/build_phase7.py:21,40`의 explicit closure/금지 목록으로 연구 atlas·original-cast-strip·baseline diagnostic 등을 제외한다. 루트 export preset의 일반 exclude만으로 모든 연구 자산이 제외된다고 가정하지 않는다.
- 글꼴은 `tools/phase7_asset_ledger.py:40` 설명상 Godot theme/OS CJK fallback이며 Windows font 파일을 복사·재배포하지 않았다. 실제 UI는 SystemFont의 Malgun Gothic/Batang 이름을 사용한다.

## 실제 API와 재사용할 코드 패턴

다음은 현재 존재하는 서명이다. 계획의 기능이 이미 지원된다고 확대 해석하지 않는다.

| 위치 | 정확한 API/패턴 | 복사·참고할 범위와 한계 |
|---|---|---|
| `expedition_view.gd:92–114` | `load_model(path:String,at:Vector3,parent:Node3D=null)->Node3D`, `find_animation(node:Node)->AnimationPlayer` | PackedScene instantiate 후 AnimationPlayer/짧은 클립명 metadata 등록. 새 rig에 동일 클립명이 있다는 보장은 없음 |
| `expedition_view.gd:116–126` | `animate(node:Node3D,clip:String,speed:float=1.0,force:bool=false,blend:float=.06)->void` | AnimationPlayer.play/advance(0), 누락 clip error. AnimationTree를 도입하면 권위를 별도 검토 |
| `presentation/actor_registry.gd:41–72,78–116` | `key(state:Dictionary)->String`, `ensure(state:Dictionary)->Node3D`, `sync(sim:RefCounted)->void` | id:generation 재사용/pose reset/수동 애니메이션/상태별클립. 현재 loader는 Skeleton_Minion.glb 하드코딩 |
| `presentation/static_batch.gd:20` | `static func batch(owner:Node3D,roots:Array[Node3D])->Dictionary` | 정적 MultiMesh batching. 서로 다른 rig나 충돌/내비를 자동 해결하지 않음 |
| `presentation/skinned_mesh_batch.gd:8` | `merge(actor:Node3D)->Dictionary` | 기존 호환성 검증된 material group 병합 패턴. 새 rig의 leaf animation을 무조건 병합하지 않음 |
| `combat/combat_resolver.gd:10,24,31` | `static damage(incoming_raw:int,hp_before_raw:int,flat_reduction_raw:int=0,resistance_bps:int=0,power_bps:int=0,death_threshold_raw:int=0)->Dictionary`; `cost(base_raw:int,cost_bps:int)->int`; `timing(startup_ticks:int,cycle_ticks:int,speed_bps:int)->Dictionary` | 정수 피해·비용·타이밍. 값/공식은 독립설계 |
| `combat/stat_block.gd:61,109` | `replace_modifiers(candidate:Variant)->bool`, `value(id_:String)->int` | 검증된 전체교체/조회 |
| `baseline_sim.gd:521–542,657` | `_make_context(id_:String)->Dictionary`, `cast_request(aim:Vector2,skill_id:String="")->bool` | 지불 시 context snapshot. 현재 선택 스킬1개 스케줄링을 독립 자동스킬 여러개로 곧바로 해석 불가 |
| `data/equipment_inventory.gd:67–100` | `reserve_item(base_id:String,quality:String)->Dictionary`, `acquire_reserved(item:Dictionary)->bool` | UID·roll RNG 예약과 소유권 이전 분리. common은affix0/crafted는정확1개 균등 후보·균등step roll |
| `data/equipment_catalog.gd:54–89` | `validate(candidate:Variant)->Array[String]` | tag/group/참조/범위 검증 패턴. 현재 SLOTS는focus/body/charm3개 |
| `data/loot_catalog.gd:17–61` | `validate(candidate:Variant)->Array[String]`, `roll(rng:RandomNumberGenerator)->Dictionary` | flat 가중치1회 추첨만. nested TC·source별table·레벨별품질 가중치는 현재 거부/미지원 |
| `baseline_sim.gd:960–985,999–1082` | `claim_death_reward(identity:Dictionary)->bool`, `_prepare_progress(candidate:Variant)->Dictionary`, `replace_progress_document(candidate:Variant)->bool` | 보상1회·전체 프로필 검증→commit. 새 chapter 저장은 별도 버전/경로 필요 |
| `presentation/expedition_effects.gd:57` | `consume(events:Array,sim:RefCounted)->void` | presentation이 사건을 수신. VFX callback에 피해 권위를 넘기지 않는 기존 패턴 |
| `presentation/expedition_audio.gd:31,34,53` | `play(cue:String,tick:int=-1)->void`, `play_ui(cue:String,tick:int)->void`, `consume(events:Array,progress_events:Array=[])->void` | 16voice 중1ambience, 나머지cue. 4tick 간격dedup. 음악/SFX/UI bus 분리 대신 현재 모든 voice별 volume 설정 |

## 구조상 필요한 확장임을 확인한 곳

- `baseline_sim.gd:343–367`의 `spawn_enemy(point:Vector2,radius:float=-1.0)->Dictionary`에는 적 definition/type 인수가 없다. HP는 공통 params.enemy_hp이고 `step_one_enemy:734–770`의 공격/이동도 공통params다. 적 정의 JSON만 추가해서3AI가 생기지 않는다.
- `run/expedition_controller.gd:121–125`의 일반 플레이 alive cap은8/16/12/20이다. 합성300적 부하가 정상 원정의 대량 전투로 구현된 상태가 아니다. spawn 간격은136–148에 별도 있다.
- `run/expedition_controller.gd:195–199`는240초 이후 정예 처치 확인으로 victory,300초까지 정예 미처치면timeout이다. 고유 보스 행동/목적지 공략 승리 구조가 아니다.
- `presentation/input_controller.gd:54–65`의 auto 요청은 현재 selected skill/nearest enemy 기반이다. 각 습득 기술별 쿨다운·다중 자동시전은 미구현이다.
- `data/progression.gd`에는 choice deck/진화 상태가 없고 `equipment_inventory.gd:115`는 equipped.size≤3이다.4슬롯 새저장/검증은 버전 설계가 필요하다.
- `presentation/expedition_world.gd:2,78`에서 장식/무충돌임을 명시하고, `baseline_sim.gd:424–427`은 목적지를 bounds clamp한다. 현재 소품은 실제 장애물이 아니다.

## 에셋북 데이터로 가져갈 수 있는 필드

기존 ledger가 실제로 제공하는 필드: `path`, `sha256`, `source`, `license`, `usage`, WAV의 `sample_rate/channels/sample_width/frames`. GLB JSON에서는 `animations[].name`, mesh 수, skin 수를 읽을 수 있다.

제작 상태·수급 여부는 이 사실을 기준으로 표시해야 한다. 예: KayKit 파일은 ‘보유/기술대역’, 세 최종 원소 효과는 ‘제작 명세 필요’, 보스는 ‘미확보/미구현’, 원작 atlas는 ‘연구 전용’. 참고작 스크린샷을 우리 제품의 보유 자산으로 표시하지 않는다.

## 확신·한계

높은 확신: 위 파일의 실제 존재/현재 코드 서명·용도·하드코딩/GLB clip 이름/WAV 헤더/동봉 license 문구. 중간 확신: 읽은 구현 범위 밖에도 추가 도구·진단이 있을 수 있으므로 모든 repo의 부재를 증명한 목록은 아니다. 미확인: 최종 자산 구매·신규 제작 소요, 새 rig/최종 VFX의 성능과 품질, 현재 소리의 청취 품질, 원작과의 계산 동일성. 기존 성공/실패 테스트나 export를 새로 실행하지 않았다.
