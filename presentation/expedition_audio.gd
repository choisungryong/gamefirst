extends RefCounted
## Original project-generated WAV cues. Bounded 16 voices; no gameplay RNG.
## https://docs.godotengine.org/en/4.5/classes/class_audiostreamplayer.html
const MAX_VOICES:=16
var voices: Array[AudioStreamPlayer]=[]
var streams: Dictionary={}
var muted:=false
var paused:=false
var master_volume:=.35
var played:=0
var dropped:=0
var last_cue_tick: Dictionary={}
var ambience: AudioStreamWAV

func setup(view: Node3D) -> void:
	for cue in ["fire","cold","lightning","impact","hurt","death","drop","pickup","equip"]:
		streams[cue]=load("res://assets/expedition/audio/"+cue+".wav")
	for i in range(MAX_VOICES):
		var voice:=AudioStreamPlayer.new()
		voice.name="ExpeditionVoice%d" % i
		view.add_child(voice)
		voices.append(voice)
	ambience=load("res://assets/expedition/audio/ambience.wav").duplicate()
	ambience.loop_mode=AudioStreamWAV.LOOP_FORWARD
	ambience.loop_begin=0
	ambience.loop_end=ambience.data.size()/2
	voices[0].stream=ambience
	voices[0].play()
	apply_volume()

func play(cue: String,tick: int=-1) -> void:
	_play_cue(cue,tick,false)

func play_ui(cue: String,tick: int) -> void:
	# UI acknowledgement may sound in a paused equipment modal; gameplay voices
	# and ambience stay paused. The same pool, mute, volume and dedup bounds apply.
	_play_cue(cue,tick,true)

func _play_cue(cue: String,tick: int,ui: bool) -> void:
	if muted or (paused and not ui) or not streams.has(cue): return
	# Repeated hits in the same crowd tick share one cue rather than pile up.
	if tick>=0 and int(last_cue_tick.get(cue,-100000))>tick-4: return
	for voice in voices.slice(1):
		if not voice.playing:
			voice.stream=streams[cue]
			voice.stream_paused=false
			voice.play()
			played+=1
			if tick>=0: last_cue_tick[cue]=tick
			return
	dropped+=1

func consume(events: Array,progress_events: Array=[]) -> void:
	for event in events:
		var tick:=int(event.get("tick",-1))
		match String(event.get("kind","")):
			"release": play(String(event.get("element","fire")),tick)
			"hit": play("impact",tick)
			"player_hurt": play("hurt",tick)
			"player_dead","enemy_dead": play("death",tick)
	for event in progress_events:
		if event.get("kind")=="loot_pickup": play("pickup",int(event.get("tick",-1)))
		elif event.get("kind")=="loot_result" and int(event.get("uid",0))>0: play("drop",int(event.get("tick",-1)))

func set_paused(value: bool) -> void:
	paused=value
	if not value and not voices[0].playing:
		voices[0].stream=ambience
		voices[0].play()
	for voice in voices: voice.stream_paused=value

func set_muted(value: bool) -> void:
	muted=value
	apply_volume()

func set_master_volume(value: float) -> void:
	if not is_finite(value): return
	master_volume=clampf(value,0,1)
	apply_volume()

func apply_volume() -> void:
	for voice in voices: voice.volume_db=linear_to_db(maxf(.0001,master_volume)) if not muted else -80

func reset() -> void:
	for voice in voices:
		voice.stop()
		voice.stream_paused=false
	last_cue_tick.clear()
