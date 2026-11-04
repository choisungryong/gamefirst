extends "res://chapter1/chapter_one_view.gd"
func _init() -> void:
 super._init();actors=load("res://chapter1/view/chapter_actors_quality25.gd").new()
func _ready() -> void:
 super._ready();set_process(false);set_physics_process(false)
 var baseline: Dictionary=run.snapshot().duplicate(true)
 var checks: Dictionary={}
 var original: Dictionary=run.enemies
 var e: Dictionary=original.values()[0].duplicate(true)
 e.kind="ranged";e.elite=false;e.hp_raw=100;e.state="move";e.frozen_until=0
 run.enemies={e.id:e};actors.reset();actors.sync(run,.016)
 var actor: Node3D=actors.actors.values()[0]
 e.hp_raw=0;e.dead_tick=run.tick
 actors.sync(run,.3)
 checks.retained_corpse_owned=actors.actors.values()[0]==actor and actor.get_parent()==self
 run.enemies={};actors.sync(run,.016)
 checks.removed_entity_pooled=actors.actors.is_empty() and actor.get_parent()==actors._pool25_root
 actor.set_meta("entity_key","obsolete");actor.set_meta("motion_sample",{"bad":true});actor.set_meta("role21_bucket",999)
 var state: Dictionary=actor.get_meta("minion19")
 state.model.rotation.x=1;state.fade=0;state.death_age=2
 for material_ in state.materials:material_.albedo_color.a=0
 var reused: Node3D=actors._create("ranged")
 checks.same_node_reused=reused==actor
 checks.detached_for_original_add=reused.get_parent()==null
 checks.transient_metadata_removed=not reused.has_meta("entity_key") and not reused.has_meta("motion_sample") and not reused.has_meta("role21_bucket")
 checks.pose_reset=state.model.rotation.is_zero_approx() and state.fade==1 and state.death_age==0
 var opaque := true
 for material_ in state.materials:opaque=opaque and material_.albedo_color.a>.99
 checks.alpha_reset=opaque
 add_child(reused);reused.queue_free()
 var elite: Node3D=actors._create("elite");add_child(elite)
 checks.elite_not_pooled=not actors._stash25(elite);elite.queue_free()
 run.enemies=original;actors.reset();actors.sync(run,0);actors.reset()
 checks.reset_active_empty=actors.actors.is_empty()
 checks.pool_bounded=actors._pool25_size()<=96
 checks.core_restored=baseline==run.snapshot()
 var file := FileAccess.open("res://pool25-fixture.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"checks":checks,"scope":"Presenter lifecycle fixture, not normal/manual/performance"},"\t"));file.close()
 audio.reset()
 for i in 4:await get_tree().process_frame
 var failed := false
 for value in checks.values():if not value:failed=true
 get_tree().quit(1 if failed else 0)
