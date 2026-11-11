extends "res://chapter1/view/chapter_elements_quality36.gd"
## Frost presentation only. Paid positions, frozen_until and inherited lifetimes
## remain authoritative. Never calls core mutation, damage, time_scale or audio.
var _frost39_projectiles: MultiMeshInstance3D
var _frost39_impacts: MultiMeshInstance3D
var _frost39_contacts: MultiMeshInstance3D
var _frost39_casts: MultiMeshInstance3D
var _frost39_seq := -1
var frost39_projectile_count := 0
var frost39_impact_count := 0
var frost39_contact_count := 0
var frost39_cast_count := 0

func setup(owner_view: Node3D) -> void:
	super.setup(owner_view)
	# These are replacement draw batches, not additional projectile/impact pools.
	# A routed frost instance is hidden in its original batch every frame.
	_frost39_projectiles=_batch(projectiles.multimesh.mesh,projectiles.multimesh.instance_count)
	_frost39_projectiles.name="FrostCore39"
	var core_material := ShaderMaterial.new()
	core_material.shader=preload("res://chapter1/view/frost_core_quality39.gdshader")
	_frost39_projectiles.material_override=core_material
	_frost39_impacts=_batch(impacts.multimesh.mesh,MAX_IMPACTS)
	_frost39_impacts.name="FrostFracture39"
	var impact_material := ShaderMaterial.new()
	impact_material.shader=preload("res://chapter1/view/frost_fracture_quality39.gdshader")
	_frost39_impacts.material_override=impact_material
	_frost39_contacts=_batch(contact_batch.multimesh.mesh,CONTACT_CAP)
	_frost39_contacts.name="FrostContact39"
	var contact_material := ShaderMaterial.new()
	contact_material.shader=preload("res://chapter1/view/frost_contact_quality39.gdshader")
	_frost39_contacts.material_override=contact_material
	var cast_shape := QuadMesh.new()
	cast_shape.size=Vector2(.60,.60)
	_frost39_casts=_batch(cast_shape,MAX_STROKES)
	_frost39_casts.name="FrostRelease39"
	var cast_material := ShaderMaterial.new()
	cast_material.shader=preload("res://chapter1/view/frost_release_quality39.gdshader")
	_frost39_casts.material_override=cast_material
	# Low-emission, depth-tested facets preserve the enemy silhouette. The four
	# inherited crystals and 128-shard pool retain their original owners/caps.
	var ice_material := StandardMaterial3D.new()
	ice_material.vertex_color_use_as_albedo=true
	ice_material.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA_DEPTH_PRE_PASS
	ice_material.albedo_color=Color(.66,.89,.96,.86)
	ice_material.metallic=.08
	ice_material.roughness=.32
	ice_material.emission_enabled=true
	ice_material.emission=Color(.06,.17,.21)
	ice_material.emission_energy_multiplier=.25
	ice_batch.material_override=ice_material
	ice_fragment_batch.material_override=ice_material
	print("CHAPTER1_FROST39 ",JSON.stringify({"scope":"presentation_only","replaces_frost_draws":true,"projectile_cap":projectiles.multimesh.instance_count,"strokes_cap":MAX_STROKES,"impacts_cap":MAX_IMPACTS,"ice_shards_cap":ICE_SHARD_CAP,"damage_owner":false}))

func consume(events: Array) -> void:
	for event in events:
		if int(event.seq)<=_frost39_seq:continue
		_frost39_seq=int(event.seq)
		if event.type!="cast" or event.get("skill_id","")!="chapter1.skill.frost":continue
		if strokes.size()>=MAX_STROKES:continue
		# Event-relative release cue; not a claimed animated hand/socket attachment.
		var direction: Vector2=event.get("direction",Vector2.RIGHT)
		strokes.append({"type":"frost39_cast","at":event.position+direction*.42,"life":.10,"duration":.10,"color":COLORS["chapter1.skill.frost"]})
	super.consume(events)

func burst(at: Vector2,color: Color,count: int,force: float=1) -> void:
	if color.is_equal_approx(COLORS["chapter1.skill.frost"]):
		# Replace the generic five-particle release with the paid cast cue. A
		# shatter already has six physical-looking shards: reduce its dust cloud.
		if count==5:return
		if count==30:count=8
	super.burst(at,color,count,force)

func sync(run: RefCounted,delta: float) -> void:
	# The inherited presenter treats every unknown stroke type as an arc and
	# reads from/to/width. Keep release cues in the same bounded stroke pool,
	# but age them here rather than exposing a new type to that legacy branch.
	var releases: Array[Dictionary]=[]
	var inherited: Array[Dictionary]=[]
	for stroke in strokes:
		if stroke.type=="frost39_cast":
			if run.mode=="playing":stroke.life-=delta
			if stroke.life>0:releases.append(stroke)
		else:inherited.append(stroke)
	strokes=inherited
	super.sync(run,delta)
	strokes.append_array(releases)
	frost39_projectile_count=_route_frost39(projectiles,_frost39_projectiles)
	frost39_impact_count=_route_frost39(impacts,_frost39_impacts)
	frost39_contact_count=_route_frost39(contact_batch,_frost39_contacts)
	frost39_cast_count=0
	var camera := view.get_viewport().get_camera_3d()
	for stroke in strokes:
		if stroke.type!="frost39_cast":continue
		if frost39_cast_count>=MAX_STROKES:break
		var at := Vector3(stroke.at.x,1.05,stroke.at.y)
		_frost39_casts.multimesh.set_instance_transform(frost39_cast_count,Transform3D(camera.global_basis,at))
		_frost39_casts.multimesh.set_instance_custom_data(frost39_cast_count,Color(1.0-float(stroke.life)/float(stroke.duration),0,0,1))
		frost39_cast_count+=1
	_frost39_casts.multimesh.visible_instance_count=frost39_cast_count

func _route_frost39(original: MultiMeshInstance3D,replacement: MultiMeshInstance3D) -> int:
	var count := 0
	for index in original.multimesh.visible_instance_count:
		var data := original.multimesh.get_instance_custom_data(index)
		if data.g<=.3 or data.g>=.8:continue
		var transform := original.multimesh.get_instance_transform(index)
		replacement.multimesh.set_instance_transform(count,transform)
		replacement.multimesh.set_instance_custom_data(count,data)
		replacement.multimesh.set_instance_color(count,original.multimesh.get_instance_color(index))
		# Parent rewrites this transform from paid state on its next sync.
		transform.basis=Basis.IDENTITY.scaled(Vector3.ZERO)
		original.multimesh.set_instance_transform(index,transform)
		count+=1
	replacement.multimesh.visible_instance_count=count
	return count

func _sync_ice(run: RefCounted,delta: float) -> void:
	super._sync_ice(run,delta)
	for index in ice_batch.multimesh.visible_instance_count:
		var transform := ice_batch.multimesh.get_instance_transform(index)
		# Narrow asymmetric blades, not an opaque shell over the whole actor.
		transform.basis=transform.basis.scaled(Vector3(.80,.88 if index%2==0 else .68,.52))
		ice_batch.multimesh.set_instance_transform(index,transform)

func _sync_fragments(run: RefCounted,delta: float) -> void:
	super._sync_fragments(run,delta)
	for index in ice_fragment_batch.multimesh.visible_instance_count:
		var transform := ice_fragment_batch.multimesh.get_instance_transform(index)
		# Inherited .48s ballistics/age stay untouched; broad splinters contrast
		# with the upright frozen state instead of spawning another burst layer.
		transform.basis=transform.basis.scaled(Vector3(1.45,.68,.42))
		ice_fragment_batch.multimesh.set_instance_transform(index,transform)

func reset() -> void:
	super.reset()
	_frost39_seq=-1
	frost39_projectile_count=0
	frost39_impact_count=0
	frost39_contact_count=0
	frost39_cast_count=0
	for batch in [_frost39_projectiles,_frost39_impacts,_frost39_contacts,_frost39_casts]:
		if is_instance_valid(batch):batch.multimesh.visible_instance_count=0
