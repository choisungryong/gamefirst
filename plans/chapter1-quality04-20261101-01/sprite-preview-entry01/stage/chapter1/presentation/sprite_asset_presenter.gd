extends Node3D
## Reusable visual presenter. Caller supplies action/direction/normalized paid phase.
## Never emits damage, changes core state, moves the actor or invents missing poses.
var sprite := Sprite3D.new()
var document: Dictionary={}
var clips: Dictionary={}
var textures: Dictionary={}
var last_sample: Dictionary={}
func configure(path: String) -> bool:
	var parsed: Variant=JSON.parse_string(FileAccess.get_file_as_string(path))
	if not parsed is Dictionary or not parsed.has("clips") or not parsed.has("frames"):return false
	document=parsed;clips=document.clips
	if sprite.get_parent()==null:add_child(sprite)
	sprite.billboard=BaseMaterial3D.BILLBOARD_ENABLED
	sprite.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return true
func sample(action: String,direction: String,phase: float) -> bool:
	var clip := action+"_"+direction
	var fallback := false
	if not clips.has(clip):clip=action
	if not clips.has(clip):clip="move_"+direction;fallback=true
	if not clips.has(clip):return false
	var indices: Array=clips[clip]
	var total := 0.0
	for index in indices:total+=float(document.frames[index].get("duration",.125))
	var normalized := fposmod(phase,1.0) if action in ["move","idle"] else clampf(phase,0,1)
	if fallback:normalized=0.0
	var elapsed := normalized*total;var local := indices.size()-1
	for i in indices.size():
		elapsed-=float(document.frames[indices[i]].get("duration",.125))
		if elapsed<0:local=i;break
	var record: Dictionary=document.frames[indices[local]]
	var path: String=record.get("texture",document.texture)
	if not textures.has(path):
		if ResourceLoader.exists(path,"Texture2D"):textures[path]=load(path)
		else:
			var image := Image.load_from_file(ProjectSettings.globalize_path(path))
			if image==null:return false
			textures[path]=ImageTexture.create_from_image(image)
	var r: Array=record.region
	var atlas := AtlasTexture.new();atlas.atlas=textures[path];atlas.region=Rect2(r[0],r[1],r[2],r[3]);atlas.filter_clip=true
	sprite.texture=atlas;sprite.pixel_size=1.0/float(record.get("pixels_per_meter",document.pixels_per_meter))
	sprite.offset=Vector2(float(r[2])*.5-float(record.feet[0]),float(record.feet[1])-float(r[3])*.5)
	last_sample={"clip":clip,"local_frame":local,"frame_index":indices[local],"fallback":fallback,"normalized_phase":normalized}
	return true
