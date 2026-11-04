extends SceneTree
func _initialize() -> void:
	var sim = preload("res://baseline_sim.gd").new()
	sim.equip_item(2)
	var document: Dictionary = sim.equipment_snapshot()
	var original: String = JSON.stringify(document)
	var parsed = JSON.parse_string(JSON.stringify(document,"\t"))
	var restored: String = JSON.stringify(parsed)
	var path: String = "res://evidence/phase5/verification/storage-probe-"+str(OS.get_process_id())+".json"
	var result: bool = sim.save_equipment(path)
	print(JSON.stringify({"equal":original == restored,"original":original,"parsed":restored,"save":result,"errors":sim.equipment_errors}))
	quit(0)
