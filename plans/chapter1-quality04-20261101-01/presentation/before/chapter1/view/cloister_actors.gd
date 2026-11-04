extends RefCounted
## New actor presentation. Geometric actors are temporary until authored sheets/models arrive.
## AnimatedSprite3D/SpriteFrames/AtlasTexture: official Godot4.5 class references.
var view: Node3D
var hero: Node3D
var actors: Dictionary = {}
var sprite_definitions: Dictionary = {}
var temporary_art := true
var _body_materials: Dictionary = {}
var _hero_previous := Vector2.INF
var _hero_move_until := -1
var _cast_until := -1
var _hit_until := -1
var _textures: Dictionary={}
var _enemy_hit_until: Dictionary={}
var raw_texture_fallbacks: Array[String]=[]
var _cast_moving_until := -1
var _cast_direction := Vector2.DOWN
var _enemy_recoil: Dictionary={}

func setup(owner_view: Node3D) -> void:
	view=owner_view
	for kind in ["hero","walker","ranged","charger","elite"]: _load_sprite(kind)
	_load_directional_casts()
	hero=_create("hero")
	view.add_child(hero)
	var marker := MeshInstance3D.new()
	var disc := TorusMesh.new();disc.inner_radius=.32;disc.outer_radius=.36;disc.rings=48;disc.ring_segments=6
	marker.mesh=disc;marker.position.y=.025;marker.scale.y=.15
	var marker_material := StandardMaterial3D.new();marker_material.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED;marker_material.albedo_color=Color(.72,.56,.31,.48);marker_material.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	marker.material_override=marker_material;hero.add_child(marker)
	temporary_art=not sprite_definitions.has("hero")

func _load_directional_casts() -> void:
	var path := "res://chapter1/art/quality03/hero_cast_v01.json"
	if not sprite_definitions.has("hero") or not FileAccess.file_exists(path):return
	var doc: Variant=JSON.parse_string(FileAccess.get_file_as_string(path))
	if not doc is Dictionary or not doc.get("frames") is Array:return
	var def: Dictionary=sprite_definitions.hero
	for direction in ["south","east","north","west"]:
		var indices: Array=doc.get("states",{}).get("cast_"+direction,doc.get("frames_by_direction",{}).get(direction,[]))
		if indices.is_empty():continue
		_add_frames(def.frames,"cast_"+direction,indices,doc,def.anchors,def.scales)
	def.directional_cast=def.frames.has_animation("cast_south") and def.frames.has_animation("cast_east") and def.frames.has_animation("cast_north") and def.frames.has_animation("cast_west")

func _load_sprite(kind: String) -> void:
	var path := "res://chapter1/art/actors/"+kind
	if not FileAccess.file_exists(path+".json"):return
	if not ResourceLoader.exists(path+".png","Texture2D") and not FileAccess.file_exists(path+".png"):return
	var doc: Variant=JSON.parse_string(FileAccess.get_file_as_string(path+".json"))
	if not doc is Dictionary: return
	var texture: Texture2D=_texture(doc.get("texture",path+".png"))
	if texture==null:return
	var frames := SpriteFrames.new()
	frames.remove_animation("default")
	if doc.get("frames") is Array and doc.get("frames_by_direction") is Dictionary:
		var anchors: Dictionary={}
		var scales: Dictionary={}
		for direction in doc.frames_by_direction:
			_add_frames(frames,"move_"+direction,doc.frames_by_direction[direction],doc,anchors,scales)
		for action in ["cast","hit","death"]:
			if not doc.get("states",{}).get(action,[]).is_empty():_add_frames(frames,action,doc.states[action],doc,anchors,scales)
		var ppm := float(doc.get("pixels_per_meter",doc.frames[0].get("pixels_per_meter",150)))
		sprite_definitions[kind]={"frames":frames,"pixel_size":1.0/ppm,"height":0.0,"anchors":anchors,"scales":scales,"directional":true}
		return
	if not doc.get("states") is Dictionary:return
	var columns := maxi(1,int(doc.get("columns",1)))
	var rows := maxi(1,int(doc.get("rows",1)))
	var cell := Vector2(float(texture.get_width())/columns,float(texture.get_height())/rows)
	for state in doc.states:
		frames.add_animation(state)
		frames.set_animation_loop(state,state!="death")
		frames.set_animation_speed(state,float(doc.get("fps",8)))
		for index in doc.states[state]:
			var atlas := AtlasTexture.new()
			atlas.atlas=texture
			atlas.region=Rect2(Vector2(int(index)%columns,int(index)/columns)*cell,cell)
			atlas.filter_clip=true
			frames.add_frame(state,atlas)
	sprite_definitions[kind]={"frames":frames,"pixel_size":1.0/float(doc.get("pixels_per_meter",250)),"height":float(doc.get("height",1.0))}

func _texture(path: String) -> Texture2D:
	if _textures.has(path):return _textures[path]
	var texture: Texture2D
	if ResourceLoader.exists(path,"Texture2D"):texture=ResourceLoader.load(path,"Texture2D") as Texture2D
	if texture==null and FileAccess.file_exists(path):
		# Unimported source-tree preview only; packaged builds must import these PNGs.
		var source := Image.load_from_file(ProjectSettings.globalize_path(path))
		if source:texture=ImageTexture.create_from_image(source);raw_texture_fallbacks.append(path)
	_textures[path]=texture
	return texture

func _add_frames(frames: SpriteFrames, animation: String, indices: Array, doc: Dictionary, anchors: Dictionary, scales: Dictionary) -> void:
	frames.add_animation(animation);frames.set_animation_loop(animation,animation.begins_with("move_"));frames.set_animation_speed(animation,8.0)
	anchors[animation]=[];scales[animation]=[]
	for index in indices:
		var record: Dictionary=doc.frames[int(index)]
		var r: Array=record.region
		var atlas := AtlasTexture.new()
		atlas.atlas=_texture(record.get("texture",doc.texture));atlas.region=Rect2(r[0],r[1],r[2],r[3]);atlas.filter_clip=true
		frames.add_frame(animation,atlas,float(record.get("duration",.125))/.125)
		var feet: Array=record.feet
		# Sprite3D offset Y points upward; feet must sit at the actor origin.
		anchors[animation].append(Vector2(float(r[2])*.5-float(feet[0]),float(feet[1])-float(r[3])*.5))
		scales[animation].append(1.0/float(record.get("pixels_per_meter",doc.pixels_per_meter)))

func consume(events: Array) -> void:
	for event in events:
		if event.type=="cast":
			_cast_until=int(event.tick)+18;_cast_moving_until=int(event.tick)+6
			_cast_direction=event.get("direction",Vector2.DOWN)
		elif event.type=="hero_hit":_hit_until=int(event.tick)+18
		elif event.type=="hit":
			_enemy_hit_until[event.target_id]=int(event.tick)+12
			# Cosmetic recoil is < .08m, substantially smaller than the .30m
			# smallest core radius; physics positions and hitboxes are never changed.
			var away: Vector2=event.position-Vector2(hero.position.x,hero.position.z)
			_enemy_recoil[event.target_id]={"until":int(event.tick)+7,"direction":away.normalized()}

func _material(color: Color) -> StandardMaterial3D:
	var key := color.to_html()
	if _body_materials.has(key): return _body_materials[key]
	var mat := StandardMaterial3D.new()
	mat.albedo_color=color
	mat.roughness=.8
	_body_materials[key]=mat
	return mat

func _part(parent: Node3D, mesh: Mesh, at: Vector3, color: Color) -> MeshInstance3D:
	var n := MeshInstance3D.new()
	n.mesh=mesh
	n.material_override=_material(color)
	n.position=at
	parent.add_child(n)
	return n

func _create(kind: String) -> Node3D:
	var actor := Node3D.new()
	actor.set_meta("kind",kind)
	if sprite_definitions.has(kind):
		var def: Dictionary=sprite_definitions[kind]
		var sprite := AnimatedSprite3D.new()
		sprite.sprite_frames=def.frames
		sprite.pixel_size=def.pixel_size
		sprite.billboard=BaseMaterial3D.BILLBOARD_ENABLED
		sprite.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		sprite.position.y=def.height
		actor.add_child(sprite)
		actor.set_meta("sprite",sprite)
		return actor
	var color: Color={"hero":Color("527f85"),"walker":Color("737466"),"ranged":Color("855b43"),"charger":Color("564f47"),"elite":Color("9f7545")}[kind]
	var height := 1.9 if kind=="hero" else (2.75 if kind=="elite" else (1.35 if kind=="charger" else 1.7))
	var pivot := Node3D.new()
	actor.add_child(pivot)
	actor.set_meta("pivot",pivot)
	var torso := CapsuleMesh.new()
	torso.radius=.24 if kind=="hero" else .28
	torso.height=height*.63
	_part(pivot,torso,Vector3(0,height*.48,0),color)
	var head := SphereMesh.new()
	head.radius=height*.095
	head.height=height*.19
	head.radial_segments=8
	head.rings=4
	_part(pivot,head,Vector3(0,height*.91,0),Color("b9afa0") if kind=="hero" else Color("8a8d7c"))
	var shoulder := BoxMesh.new()
	shoulder.size=Vector3(.65 if kind!="elite" else .9,.17,.28)
	_part(pivot,shoulder,Vector3(0,height*.71,0),color.lightened(.1))
	if kind=="hero" or kind=="ranged":
		var staff := CylinderMesh.new()
		staff.top_radius=.035
		staff.bottom_radius=.04
		staff.height=height*.9
		_part(pivot,staff,Vector3(.38,height*.5,.1),Color("6f5840"))
		var jewel := SphereMesh.new()
		jewel.radius=.10
		jewel.height=.20
		_part(pivot,jewel,Vector3(.38,height*.98,.1),Color("80cad5") if kind=="hero" else Color("cb7750"))
	elif kind=="charger" or kind=="elite":
		var horns := PrismMesh.new()
		horns.size=Vector3(.7,height*.38,.3)
		_part(pivot,horns,Vector3(0,height*.92,.02),Color("b3aa89"))
	return actor

func sync(run: RefCounted, delta: float) -> void:
	if run.hero.is_empty(): return
	hero.position=Vector3(run.hero.position.x,0,run.hero.position.y)
	if _hero_previous!=run.hero.position:
		_hero_move_until=run.tick+2
		_hero_previous=run.hero.position
	var briefly_casting: bool=run.tick<_cast_moving_until and sprite_definitions.get("hero",{}).get("directional_cast",false)
	var hero_moving: bool=run.tick<_hero_move_until
	var cast_facing: bool=run.tick<_cast_until and sprite_definitions.get("hero",{}).get("directional_cast",false) and (not hero_moving or briefly_casting)
	_update_pose(hero,_cast_direction if cast_facing else run.hero.direction,hero_moving,run.tick<_cast_until,run.hero.hp_raw<=0,run.tick,run.mode in ["playing","defeat"],run.tick<_hit_until,briefly_casting)
	if hero.has_meta("sprite"):
		var hero_sprite: AnimatedSprite3D=hero.get_meta("sprite")
		hero_sprite.scale=Vector3.ONE*1.10
	for id_ in _enemy_hit_until.keys():
		if run.tick>=int(_enemy_hit_until[id_]):_enemy_hit_until.erase(id_)
	for id_ in _enemy_recoil.keys():
		if run.tick>=int(_enemy_recoil[id_].until):_enemy_recoil.erase(id_)
	var wanted: Dictionary={}
	for e in run.enemies.values():
		var key: String="%d:%d" % [e.generation,e.id]
		wanted[key]=true
		if not actors.has(key):
			actors[key]=_create(e.kind)
			view.add_child(actors[key])
		var actor: Node3D=actors[key]
		actor.position=Vector3(e.position.x,0,e.position.y)
		var dead: bool=e.hp_raw<=0
		if not dead and _enemy_recoil.has(e.id):
			var recoil: Dictionary=_enemy_recoil[e.id]
			var remaining: float=clampf(float(int(recoil.until)-run.tick)/7.0,0,1)
			actor.position+=Vector3(recoil.direction.x,0,recoil.direction.y)*(.075*sin(remaining*PI))
		var frozen: bool=run.tick<int(e.frozen_until)
		_update_pose(actor,e.attack_direction if e.state in ["windup","dash"] else e.direction,e.state=="move",e.state=="windup",dead,run.tick,run.mode=="playing" and not frozen,run.tick<int(_enemy_hit_until.get(e.id,-1)))
		if actor.has_meta("sprite"):
			var sprite: AnimatedSprite3D=actor.get_meta("sprite")
			var hit_left: int=int(_enemy_hit_until.get(e.id,-1))-run.tick
			sprite.modulate=Color(.55,.88,1.05) if frozen else (Color(1.25,1.13,.97) if hit_left>9 else Color.WHITE)
		if dead:
			# Keep the body its authored size. A corpse fades after its collapse,
			# rather than shrinking into a toy-sized upright actor.
			actor.scale=Vector3.ONE
			if actor.has_meta("sprite"):
				var corpse: AnimatedSprite3D=actor.get_meta("sprite")
				corpse.modulate.a=1.0-clampf(float(run.tick-int(e.dead_tick)-36)/39.0,0,1)
		else: actor.scale=Vector3.ONE
	for key in actors.keys():
		if not wanted.has(key):
			actors[key].queue_free()
			actors.erase(key)

func _update_pose(actor: Node3D, direction: Vector2, moving: bool, casting: bool, dead: bool, tick: int, playing: bool, hit: bool=false, brief_cast: bool=false) -> void:
	if actor.has_meta("sprite"):
		var sprite: AnimatedSprite3D=actor.get_meta("sprite")
		var def: Dictionary=sprite_definitions[actor.get_meta("kind")]
		var state := "death" if dead else ("cast" if casting else ("move" if moving else "idle"))
		if def.get("directional",false):
			var camera := view.get_viewport().get_camera_3d()
			var right := Vector2(camera.global_basis.x.x,camera.global_basis.x.z).normalized()
			var forward := Vector2(-camera.global_basis.z.x,-camera.global_basis.z.z).normalized()
			var screen := Vector2(direction.dot(right),-direction.dot(forward))
			var facing := ("east" if screen.x>0 else "west") if absf(screen.x)>absf(screen.y) else ("south" if screen.y>0 else "north")
			state="move_"+facing
			# Authored action sheet currently faces south. Use it while planted;
			# moving retains directional gait rather than snapping orientation.
			if dead and sprite.sprite_frames.has_animation("death"):state="death"
			# Legacy hurt/attack strips face south. Preserve a north/east/west
			# silhouette instead of snapping every struck traveler toward camera.
			# Flash/recoil still conveys those hits; authored directional casts win.
			elif hit and facing=="south" and sprite.sprite_frames.has_animation("hit"):state="hit"
			elif casting and (not moving or brief_cast):
				if def.get("directional_cast",false) and sprite.sprite_frames.has_animation("cast_"+facing):state="cast_"+facing
				elif not moving and facing=="south" and sprite.sprite_frames.has_animation("cast"):state="cast"
		if not sprite.sprite_frames.has_animation(state): state="idle"
		if sprite.sprite_frames.has_animation(state) and sprite.animation!=state: sprite.play(state)
		sprite.speed_scale=1.0 if playing and (moving or state in ["cast","hit","death"] or state.begins_with("cast_")) else 0.0
		if brief_cast and moving and state.begins_with("cast_"):
			# Six simulation ticks show a directional release silhouette while
			# traveling. The planted clip can play fully without a .3s foot glide.
			sprite.frame=mini(2,sprite.sprite_frames.get_frame_count(state)-1);sprite.speed_scale=0.0
		if def.get("directional",false):
			if not moving and state.begins_with("move_"):sprite.frame=0
			sprite.offset=def.anchors[state][sprite.frame]
			sprite.pixel_size=def.scales[state][sprite.frame]
		else:sprite.flip_h=direction.x<-.1
	else:
		var pivot: Node3D=actor.get_meta("pivot")
		actor.rotation.y=atan2(direction.x,direction.y)
		pivot.rotation.x=PI*.47 if dead else (sin(float(tick)*.24)*.045 if moving else -.06 if casting else 0.0)
		pivot.position.y=absf(sin(float(tick)*.22))*.045 if moving and not dead else 0.0

func reset() -> void:
	for actor in actors.values(): actor.queue_free()
	actors.clear()
	_hero_previous=Vector2.INF;_hero_move_until=-1
	_cast_until=-1;_hit_until=-1
	_enemy_hit_until.clear()
	_cast_moving_until=-1;_cast_direction=Vector2.DOWN;_enemy_recoil.clear()
