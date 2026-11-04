extends "res://chapter1/presentation/sprite_asset_presenter.gd"
## Immutable shared atlas resources; per-actor playback state remains independent.
static var _catalogs: Dictionary={}
var _frames: Array=[]
var _durations: Dictionary={}
func configure(path: String) -> bool:
	if not _catalogs.has(path):
		if not super.configure(path):return false
		var frames_: Array=[];var durations_: Dictionary={}
		for record in document.frames:
			var texture_path: String=record.get("texture",document.texture)
			if not textures.has(texture_path):
				if ResourceLoader.exists(texture_path,"Texture2D"):textures[texture_path]=load(texture_path)
				else:
					var image := Image.load_from_file(ProjectSettings.globalize_path(texture_path))
					if image==null:return false
					textures[texture_path]=ImageTexture.create_from_image(image)
			var r: Array=record.region
			var atlas := AtlasTexture.new();atlas.atlas=textures[texture_path];atlas.region=Rect2(r[0],r[1],r[2],r[3]);atlas.filter_clip=true
			frames_.append({"texture":atlas,"offset":Vector2(float(r[2])*.5-float(record.feet[0]),float(record.feet[1])-float(r[3])*.5),"pixel_size":1.0/float(record.get("pixels_per_meter",document.pixels_per_meter))})
		for clip in clips:
			var total := 0.0
			for index in clips[clip]:total+=float(document.frames[index].get("duration",.125))
			durations_[clip]=total
		_catalogs[path]={"document":document,"frames":frames_,"durations":durations_}
	var catalog: Dictionary=_catalogs[path];document=catalog.document;clips=document.clips;_frames=catalog.frames;_durations=catalog.durations
	if sprite.get_parent()==null:add_child(sprite)
	sprite.billboard=BaseMaterial3D.BILLBOARD_ENABLED;sprite.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	sprite.alpha_cut=SpriteBase3D.ALPHA_CUT_OPAQUE_PREPASS;sprite.layers=2
	return true
func key_for(action: String,direction: String) -> String:
	if clips.has(action+"_"+direction):return action+"_"+direction
	return action if clips.has(action) else "move_"+direction
func duration_for(action: String,direction: String) -> float:return float(_durations.get(key_for(action,direction),.125))
func release_phase(direction: String,release_frame: int) -> float:
	var key := key_for("cast",direction);var ids: Array=clips[key];var total: float=_durations[key];var before := 0.0
	for i in mini(release_frame,ids.size()):before+=float(document.frames[ids[i]].get("duration",.125))
	return before/total
func sample(action: String,direction: String,phase: float) -> bool:
	var key := key_for(action,direction)
	if not clips.has(key):return false
	var fallback: bool=key.begins_with("move_") and action!="move"
	var indices: Array=clips[key]
	var normalized := fposmod(phase,1.0) if action in ["move","idle"] else clampf(phase,0,1)
	if fallback:normalized=0
	var elapsed: float=normalized*float(_durations[key]);var local := indices.size()-1
	for i in indices.size():
		elapsed-=float(document.frames[indices[i]].get("duration",.125))
		if elapsed<0:local=i;break
	var index: int=indices[local];var frame: Dictionary=_frames[index]
	sprite.texture=frame.texture;sprite.pixel_size=frame.pixel_size;sprite.offset=frame.offset
	last_sample={"clip":key,"local_frame":local,"frame_index":index,"fallback":fallback,"normalized_phase":normalized}
	return true
static func clear_shared_cache() -> void:
	## Preview host calls only after all bound actors have been freed.
	_catalogs.clear()
