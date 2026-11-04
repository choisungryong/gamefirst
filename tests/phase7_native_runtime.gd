extends SceneTree
## Candidate PCK, real OS input, storage-path isolation only. No combat fixtures.
const Run=preload("res://run/expedition_controller.gd")
class IsolatedSim:
	extends "res://baseline_sim.gd"
	var isolated_path := ""
	func save_progress(_path: String="") -> bool: return super.save_progress(isolated_path)
	func load_progress(_path: String="") -> bool: return super.load_progress(isolated_path)
var output := ""
var expected := ""
var view: Node
var snapshots: Array=[]
var elapsed := 0.0
var last_second := -1
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--native-output="): output=arg.trim_prefix("--native-output=")
		elif arg.begins_with("--expected-metadata="): expected=arg.trim_prefix("--expected-metadata=")
	call_deferred("run")
func run() -> void:
	if output.is_empty() or not output.replace("\\","/").contains("/evidence/phase7/") or DirAccess.dir_exists_absolute(output) or expected.is_empty() or FileAccess.get_sha256("res://game_data/build_info.json")!=expected:
		quit(1)
		return
	DirAccess.make_dir_recursive_absolute(output)
	view=load("res://Expedition.tscn").instantiate()
	var isolated=IsolatedSim.new()
	isolated.isolated_path="res://evidence/phase7/native-runtime/"+str(OS.get_process_id())+"/progress.json"
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(isolated.isolated_path.get_base_dir()))
	view.sim=isolated
	view.controller=Run.new(isolated)
	root.add_child(view)
	root.tree_exiting.connect(save)
	print("NATIVE_RUNTIME_READY: actual UI input; storage path only isolated; "+isolated.isolated_path)
func _process(delta: float) -> bool:
	elapsed+=delta
	if is_instance_valid(view) and int(elapsed)!=last_second:
		last_second=int(elapsed)
		snapshots.append({"wall_seconds":elapsed,"run":view.controller.snapshot(),"life":view.sim.life,"mana_raw":view.sim.mana_raw,"profile":view.sim.progress_document(),"modal":view.is_equipment_open(),"auto":view.input_controller.auto_cast,"skill":view.sim.selected_skill_id,"muted":view.audio.muted,"volume":view.audio.master_volume,"audio_played":view.audio.played,"notice":view.equipment_presenter.notice_label.text})
		save()
	return false
func save() -> void:
	if output.is_empty(): return
	var file:=FileAccess.open(output.path_join("snapshots.json"),FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify({"scope":"OS input, isolated save path only; screenshots remain Computer Use observations", "metadata_sha256":expected,"executable":OS.get_executable_path(),"external_script_sha256":FileAccess.get_sha256(get_script().resource_path),"snapshots":snapshots},"\t"))
		file.close()
