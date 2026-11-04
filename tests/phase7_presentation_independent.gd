extends SceneTree
## Independent bounded-presenter probes. Synthetic FX/loot loads are not gameplay.
var checks := 0
var failures: Array[String] = []
func _initialize() -> void: call_deferred("run")
func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures.append(message)
		printerr("PHASE7 PRESENTATION FAILED: "+message)
func authority(sim: RefCounted) -> Dictionary:
	return {"profile":sim.progress_document(),"damage_rng":str(sim.rng.state),"tick":sim.tick,"life":sim.life,"mana":sim.mana_raw,"pending":sim.pending_context_snapshot(),"combat":sim.history.duplicate(true)}
func run() -> void:
	var packed: PackedScene=load("res://Expedition.tscn")
	var view=packed.instantiate()
	root.add_child(view)
	view.set_process(false)
	view.set_physics_process(false)
	await process_frame
	await process_frame
	check(view.audio.voices.size()==16,"audio creates exactly16 bounded voices")
	check(view.audio.streams.size()==9,"all nine original sound cues load")
	check(view.audio.ambience is AudioStreamWAV and view.audio.ambience.loop_mode==AudioStreamWAV.LOOP_FORWARD,"original ambience stream loops")
	for cue in view.audio.streams: check(view.audio.streams[cue] is AudioStreamWAV,"cue is decoded PCM WAV "+cue)
	var before: Dictionary=authority(view.sim)
	view.audio.set_paused(false)
	view.audio.set_muted(false)
	view.audio.reset()
	for i in range(100): view.audio.play("impact")
	check(view.audio.voices.size()==16,"crowd audio spam cannot create extra voices")
	view.audio.set_paused(true)
	var played: int=view.audio.played
	view.audio.play("fire")
	check(view.audio.played==played,"paused audio suppresses new playback")
	var paused_all:=true
	# Godot reports stream_paused=false for a stopped voice (including dummy audio).
	for voice in view.audio.voices: paused_all=paused_all and (voice.stream_paused or not voice.playing)
	check(paused_all and view.audio.paused,"pause reaches every currently active audio voice")
	view.audio.set_paused(false)
	view.audio.set_muted(true)
	view.audio.play("fire")
	check(view.audio.played==played,"mute suppresses new playback")
	view.audio.set_master_volume(-1)
	check(view.audio.master_volume==0,"master volume lower bound")
	view.audio.set_master_volume(2)
	check(view.audio.master_volume==1,"master volume upper bound")
	view.audio.set_master_volume(NAN)
	check(view.audio.master_volume==1,"nonfinite volume preserves valid setting")
	view.audio.reset()
	check(view.audio.last_cue_tick.is_empty(),"audio reset clears crowd rate-limit history")
	view.audio.set_muted(false)
	view.audio.set_paused(false)
	check(view.audio.voices[0].stream==view.audio.ambience,"resume restores reserved ambience voice")
	played=view.audio.played
	for i in range(10): view.audio.play("impact",100)
	check(view.audio.played==played+1,"same-tick crowd impacts share one sound cue")
	check(view.audio.voices[0].stream==view.audio.ambience,"effect sounds never steal reserved ambience voice")
	view.hud.volume_slider.value=.62
	check(is_equal_approx(view.audio.master_volume,.62),"actual HUD volume signal updates master gain")
	view.effects.burst(Vector3.ZERO,"fire",2000,.2)
	check(view.effects.created==160 and view.effects.active.size()==160 and view.effects.dropped>0,"transient spam is capped at160 with explicit drops")
	view.effects.sync(view.sim,1)
	check(view.effects.active.is_empty() and view.effects.pool.size()==160,"expired transient nodes return to bounded pool")
	view.effects.burst(Vector3.ZERO,"cold",160,.2)
	check(view.effects.created==160 and view.effects.pool.is_empty(),"transient reuse creates no additional nodes")
	view.effects.reset()
	view.effects.reset()
	check(view.effects.active.is_empty() and view.effects.pool.size()==160,"repeated FX reset cannot duplicate pooled nodes")
	check(authority(view.sim)==before,"audio and transient projection cannot change combat/profile/RNG")
	# This intentionally oversized synthetic projectile list tests only presentation cap.
	for i in range(150): view.sim.bolts.append({"id":i+1,"p":Vector2.ZERO,"direction":Vector2.RIGHT})
	view.effects.sync(view.sim,0)
	check(view.effects.projectiles.size()==128 and view.effects.projectile_created==128,"projectile projection bounded128 even with oversized input")
	view.sim.bolts.clear()
	view.effects.sync(view.sim,0)
	check(view.effects.projectiles.is_empty() and view.effects.projectile_pool.size()==128,"projectile removal returns all nodes")
	view.effects.reset()
	check(view.effects.projectile_pool.size()==128,"repeated projectile reset does not duplicate pool")
	# Reserve shared UIDs, with 33 entries deliberately exceeding the real core cap32.
	for i in range(33):
		var item: Dictionary=view.sim.equipment_inventory.reserve_item("item.ember_focus","common")
		view.sim._ground_loot[int(item.uid)]={"item":item,"p":[0.0,0.0],"expires":view.sim.tick+1800}
	before=authority(view.sim)
	view.loot.sync(view.sim,view.camera)
	check(view.loot.markers.size()==32 and view.loot.labels.size()==32,"loot projection independently caps oversized snapshot32")
	check(authority(view.sim)==before,"loot projection preserves profile allocation/RNG and combat")
	var stale_keys: Array=view.loot.markers.keys()
	view.sim._loot_epoch+=1
	view.loot.sync(view.sim,view.camera)
	var overlap:=false
	for key in stale_keys: overlap=overlap or view.loot.markers.has(key)
	check(not overlap and view.loot.markers.size()==32,"epoch change invalidates all old marker identities")
	view.loot.reset()
	check(view.loot.markers.is_empty() and view.loot.labels.is_empty(),"loot reset clears both marker and label maps")
	view.sim._ground_loot.clear()
	view.free()
	await process_frame
	await process_frame
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional phase7 presentation harness failure proof")
	print(JSON.stringify({"scope":"Headless independent bounded audio/FX/loot presenter probes; synthetic oversize inputs explicit; no GPU/art/audio-listening claim","checks":checks,"failures":failures,"success":failures.is_empty()}))
	quit(0 if failures.is_empty() else 1)
