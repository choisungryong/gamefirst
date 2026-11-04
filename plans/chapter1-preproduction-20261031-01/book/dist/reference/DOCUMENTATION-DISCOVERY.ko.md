# Phase0 문서·기존 API 탐색 결과

2026-10-30. make-plan 지침에 따라 사실 수집을 분담했고 계획 작성은 root가 수행했다. 아래는 읽은 실제 코드/공식 Godot4.5 문서의 사용 가능한 패턴이다. 새 API의 구현·새 성능을 주장하지 않는다.

## 기존 코어에서 재사용할 경계

| 위치 | 실제 API/패턴 |
|---|---|
| combat/combat_resolver.gd:10 | damage(incoming_raw:int,hp_before_raw:int,flat_reduction_raw:int=0,resistance_bps:int=0,power_bps:int=0,death_threshold_raw:int=0)->Dictionary |
| combat/stat_block.gd:61,109 | replace_modifiers(candidate:Variant)->bool, value(id_:String)->int. 검증 후 교체·최대64modifier |
| baseline_sim.gd:521–542,657 | _make_context(id_:String)->Dictionary, cast_request(aim:Vector2,skill_id:String="")->bool. 지불 시점 context snapshot |
| data/equipment_inventory.gd:67,88 | reserve_item(base_id:String,quality:String)->Dictionary, acquire_reserved(item:Dictionary)->bool. UID·아이템 RNG와 소유권 이전 |
| data/equipment_inventory.gd:165,198,208 | replace_document(candidate:Variant)->bool, equip(uid:int)->bool, unequip(slot:String)->bool |
| data/loot_catalog.gd:17,53 | validate(candidate:Variant)->Array[String], roll(rng:RandomNumberGenerator)->Dictionary. 현재flat1단계만 |
| baseline_sim.gd:921–985,999–1082 | ground/handle/claim/전체profile 준비→commit. 사망 중복·epoch·현재량 무회복 경계 |
| presentation/static_batch.gd:20–42 | 기존 MultiMesh 정적 batching 패턴 |

## 확장 전에 알아야 할 실제 공백

- spawn_enemy(point:Vector2,radius:float=-1.0)->Dictionary에는 적 type/definition 인수가 없다(baseline_sim.gd:343–367). step_one_enemy:734–770도 공통 params. 적별 데이터를 추가하기만 해서는 다른 행동이 생기지 않는다.
- 현재 정예는 run/expedition_controller.gd:179–185의54HP 변경과 표현이다. 보스·범위 전조 handler는 새 명세·구현 대상이다.
- data/progression.gd:6–13은 레벨1/2/3·장비 해금이다. 성장 deck/트리/진화/시너지 선택은 새 작업이다.
- affix 자격 tag/group 검증은 이미 있지만 crafted 정확1개 균등 선택이다. weighted 후보/품질·레벨별pool/복수옵션/조건부 발동은 새 작업이다.
- equipment_presenter.gd:125–159는 modifier 문자열 목록이다. 비교 장착·전투 효과 차이 계산은 별도다.
- 현재 이동은 bounds clamp와 클릭 지면 plane이다. 장식 벽/지형에 전투 충돌이 있다고 가정하지 않는다.
- 원정의 모델은 KayKit 기술 대역, 효과는 Sphere/Torus/Cylinder, 음향은 자체 합성 cue/ambience다. 새 고품질 자산의 공급 비용/기간/성능은 미확인이다.

## 공식 문서에서 읽어 확인한 허용 패턴

### 입자·재질 곡선

[GPUParticles3D](https://docs.godotengine.org/en/4.5/classes/class_gpuparticles3d.html)의 restart(keep_seed:bool=false), one_shot, finished, process_material, lifetime, amount_ratio, set_draw_pass_mesh(pass:int,mesh:Mesh)를 확인했다. 반복 one-shot의 GPU 지연을 고려하며 finished는one_shot=false에서 발생하지 않는다.

[ParticleProcessMaterial 튜토리얼](https://docs.godotengine.org/en/4.5/tutorials/3d/particles/process_material_properties.html)의 Min/max/curve 및 Initial velocity 절을 제작 패턴으로 읽는다. 방향만 주고 속도/가속도 없이 움직일 것으로 가정하지 않는다. [CurveTexture](https://docs.godotengine.org/en/4.5/classes/class_curvetexture.html)의 curve/texture_mode/width를 확인했다. API 도입 자체는 효과 품질 증거가 아니다.

### 애니메이션 혼합

[Using AnimationTree](https://docs.godotengine.org/en/4.5/tutorials/animation/animation_tree.html)의 Creating a tree / Blend2·Blend3 / OneShot 예제를 읽는다. 실제 예제는 animation_tree.set("parameters/OneShot/request", AnimationNodeOneShot.ONE_SHOT_REQUEST_FIRE)다. OneShot은 자신이 만든 노드명과 같아야 한다.

[AnimationTree 문서](https://docs.godotengine.org/en/4.5/classes/class_animationtree.html)에 따라 tree와 AnimationPlayer가 동시에 재생 권위를 갖지 않게 한다. 현재제품의 AnimationPlayer.play 경로를 그대로 남기고 tree만 덧붙이지 않는다. deprecated set_process_callback을 새 도입 경로로 삼지 않고 AnimationMixer.callback_mode_process를 확인한다.

### 음향

[AudioServer](https://docs.godotengine.org/en/4.5/classes/class_audioserver.html)의 get_bus_index(bus_name:StringName)->int, set_bus_volume_db(bus_idx:int,volume_db:float), set_bus_volume_linear(bus_idx:int,volume_linear:float), set_bus_mute(bus_idx:int,enable:bool)를 확인했다. Audio buses 튜토리얼 패턴으로 음악/SFX/UI 구분을 설계한다. 기존voice pool 상한과 버스 설계는 다른 문제다.

### 길찾기와 군중

[Using NavigationAgents](https://docs.godotengine.org/en/4.5/tutorials/navigation/navigation_using_navigationagents.html)의 Node3D GDScript 예제에서 set_target_position(Vector3), is_navigation_finished(), get_next_path_position(), velocity_computed, set_velocity(Vector3)를 확인했다. Agent가 actor를 자동 이동시키지는 않는다. map 동기화 전 query를 피한다. 현재Vector2고정tick코어를 무조건 대체하지 말고 실제 장애물/결정성/비용을 검토해 채택한다.

[MultiMesh](https://docs.godotengine.org/en/4.5/classes/class_multimesh.html)의 transform_format, instance_count, custom_aabb, visible_instance_count, set_instance_transform(instance:int,transform:Transform3D)를 확인했다. 개별instance culling/임의리그 자동해결로 해석하지 않는다. 기존 정적 batching 패턴을 먼저 재사용한다.

## 확인 한계

코드·문서의 구조/서명은 확인했지만 이번 계획 작업에서 새GPU실행·청취·D2R디컴파일은 하지 않았다. 여러 고급 API를 모두 도입해야 한다는 결론도 아니다. 새로운 자산·입자·경로·시너지의 실기 비용은 대표 장면에서 측정한다. REA를 통한 참고작 제작 과정과 비공개 소스는 별도로 확인되지 않았다.
