extends SceneTree
## Generic JSON serializer/hash oracle. No project implementation is imported.
## Frozen JSON bytes alone are read; this reproduces the documented encoding
## contract with the pinned engine's JSON serializer, not EquipmentCatalog code.
func _initialize() -> void:
	var source_root := ""
	var output := ""
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--source="): source_root = argument.trim_prefix("--source=")
		elif argument.begins_with("--output="): output = argument.trim_prefix("--output=")
	if source_root.is_empty() or output.is_empty() or FileAccess.file_exists(output):
		printerr("Oracle requires a frozen source and a new output path")
		quit(1)
		return
	var catalog_path: String = source_root.path_join("game_data/catalog.json")
	var equipment_path: String = source_root.path_join("game_data/equipment.json")
	var catalog_parser := JSON.new()
	var equipment_parser := JSON.new()
	if catalog_parser.parse(FileAccess.get_file_as_string(catalog_path)) != OK or equipment_parser.parse(FileAccess.get_file_as_string(equipment_path)) != OK:
		quit(1)
		return
	var catalog: Dictionary = catalog_parser.data
	var stats: Dictionary = {}
	for definition in catalog.stats: stats[definition.id] = definition.duplicate(true)
	var combat_hash: String = JSON.stringify(catalog,"",true,true).sha256_text()
	var fingerprint: String = JSON.stringify({"equipment":equipment_parser.data,"stats":stats,"combat_rules":combat_hash},"",true,true).sha256_text()
	var report := {"scope":"Frozen JSON generic serializer/hash oracle; no product scripts imported","engine":Engine.get_version_info().string,"catalog_sha256":FileAccess.get_sha256(catalog_path),"equipment_sha256":FileAccess.get_sha256(equipment_path),"combat_rules_fingerprint":combat_hash,"equipment_content_fingerprint":fingerprint,"oracle_script_sha256":FileAccess.get_sha256(get_script().resource_path)}
	var file := FileAccess.open(output,FileAccess.WRITE)
	if not file:
		quit(1)
		return
	file.store_string(JSON.stringify(report,"\t"))
	file.flush()
	var success: bool = file.get_error() == OK
	print(JSON.stringify({"success":success,"fingerprint":fingerprint}))
	quit(0 if success else 1)
