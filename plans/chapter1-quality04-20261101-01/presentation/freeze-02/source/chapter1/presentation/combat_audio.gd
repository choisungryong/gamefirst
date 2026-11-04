extends RefCounted
## Licensed Kenney CC0 foley/spell layers; source/processing ledger is beside WAVs.
## AudioStreamPlayer API: https://docs.godotengine.org/en/4.5/classes/class_audiostreamplayer.html
## Twelve one-shot voices + one quiet loop. Worst aligned source peaks stay <1.
const MAX_VOICES := 13
const PATH := "res://chapter1/art/quality03_audio/"
const COUNTS := {"fire":3,"cold":2,"lightning":1,"impact":3,"death":3,"explosion":1,"hurt":1,"drop":1,"pickup":1,"equip":1,"step":2}
const COOLDOWNS := {"fire":10,"cold":14,"lightning":14,"impact":7,"death":10,"explosion":14,"hurt":18,"drop":18,"pickup":8,"equip":4,"step":18}
const GAINS := {"fire":.8,"cold":.72,"lightning":.82,"impact":.9,"death":.65,"explosion":1.0,"hurt":1.0,"drop":.8,"pickup":.65,"equip":.75,"step":.38}
var voices: Array[AudioStreamPlayer]=[]
var streams: Dictionary={}
var ambience: AudioStreamWAV
var muted := false
var paused := true
var master_volume := .8
var played := 0
var dropped := 0
var last_cue_tick: Dictionary={}
var variants: Dictionary={}
var raw_fallbacks: Array[String]=[]
var voice_gains: Array[float]=[]

func setup(view: Node3D) -> void:
	for cue in COUNTS:
		var options: Array[AudioStream]=[]
		for i in int(COUNTS[cue]):options.append(_load_wav(PATH+cue+"_%d.wav" % i))
		streams[cue]=options
	for i in MAX_VOICES:
		var voice := AudioStreamPlayer.new()
		voice.name="Chapter1CombatVoice%d" % i
		view.add_child(voice);voices.append(voice)
		voice_gains.append(1.0)
	ambience=_load_wav(PATH+"ambience.wav").duplicate()
	ambience.loop_mode=AudioStreamWAV.LOOP_FORWARD
	ambience.loop_begin=0;ambience.loop_end=ambience.data.size()/2
	voices[0].stream=ambience
	apply_volume()
	print("CHAPTER1_AUDIO ",JSON.stringify({"licensed_variants":19,"voices":MAX_VOICES,"raw_fallbacks":raw_fallbacks,"ledger":PATH+"AUDIO-LEDGER.json"}))

func _load_wav(path: String) -> AudioStreamWAV:
	if ResourceLoader.exists(path,"AudioStreamWAV"):return ResourceLoader.load(path,"AudioStreamWAV") as AudioStreamWAV
	# Source-tree preview only. Exports must use imported resources (fallbacks=[]).
	# https://docs.godotengine.org/en/4.5/classes/class_audiostreamwav.html#class-audiostreamwav-method-load-from-file
	if FileAccess.file_exists(path):
		raw_fallbacks.append(path)
		return AudioStreamWAV.load_from_file(ProjectSettings.globalize_path(path))
	push_error("Missing Chapter1 audio resource: "+path)
	return null

func play(cue: String,tick: int=-1) -> void:
	_play_cue(cue,tick,false)

func play_ui(cue: String,tick: int) -> void:
	_play_cue(cue,tick,true)

func _play_cue(cue: String,tick: int,ui: bool) -> void:
	if muted or (paused and not ui) or not streams.has(cue):return
	if tick>=0 and tick-int(last_cue_tick.get(cue,-100000))<int(COOLDOWNS[cue]):return
	# Two final voices remain available for player hurt and important loot/UI cues.
	var critical: bool=cue in ["hurt","drop","equip","pickup"]
	var end := MAX_VOICES if critical else MAX_VOICES-2
	for index in range(1,end):
		var voice := voices[index]
		if voice.playing:continue
		var variant: int=int(variants.get(cue,0))%int(COUNTS[cue])
		variants[cue]=variant+1
		voice.stream=streams[cue][variant]
		voice.pitch_scale=[.97,1.0,1.035][variant%3]
		voice_gains[index]=float(GAINS[cue])
		voice.volume_db=linear_to_db(maxf(.0001,master_volume*.11*voice_gains[index]))
		voice.stream_paused=false;voice.play()
		played+=1
		if tick>=0:last_cue_tick[cue]=tick
		return
	dropped+=1

func set_paused(value: bool) -> void:
	if paused==value:return
	paused=value
	if not value and not voices[0].playing:
		voices[0].stream=ambience;voices[0].play()
	for voice in voices:voice.stream_paused=value

func set_muted(value: bool) -> void:
	muted=value;apply_volume()

func set_master_volume(value: float) -> void:
	if not is_finite(value):return
	master_volume=clampf(value,0,1);apply_volume()

func apply_volume() -> void:
	for index in voices.size():
		# Individual peaks<=.68 *12voices*.11 =.8976 at master1.
		# Looppeak<=.22*.025 adds.0055, so even worst phase alignment stays bounded.
		var gain := .025 if index==0 else .11*voice_gains[index]
		voices[index].volume_db=linear_to_db(maxf(.0001,master_volume*gain)) if not muted else -80

func reset() -> void:
	for voice in voices:voice.stop();voice.stream_paused=false
	voice_gains.fill(1.0)
	last_cue_tick.clear();variants.clear();paused=true
