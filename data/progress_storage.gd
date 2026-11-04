extends RefCounted
## Checked original copy plus sibling replacement. No power-loss or concurrent
## writer durability guarantee; the original backup is retained on every path.
## Official 4.5 API signatures:
## https://docs.godotengine.org/en/4.5/classes/class_diraccess.html#class-diraccess-method-rename-absolute
## https://docs.godotengine.org/en/4.5/classes/class_fileaccess.html#class-fileaccess-method-flush
const PATH := "user://progress-v1.json"
const TEST_ROOT := "res://evidence/phase6/"
var errors: Array[String] = []

func allowed_path(path: String) -> bool:
	if path == PATH: return true
	if not path.ends_with(".json") or path.contains("\\") or path.contains("..") or path.contains("\n") or path.contains("\r"): return false
	var resolved: String = ProjectSettings.globalize_path(path).simplify_path()
	for test_root in [TEST_ROOT,"res://evidence/phase7/"]:
		var root: String = ProjectSettings.globalize_path(test_root).simplify_path().trim_suffix("/")+"/"
		if path.begins_with(test_root) and resolved.begins_with(root): return true
	return false

func read_document(path: String = PATH) -> Variant:
	errors.clear()
	if not allowed_path(path):
		errors.assign(["Unsupported progress save path"])
		return null
	var file := FileAccess.open(path,FileAccess.READ)
	if file == null or file.get_length() > 1048576:
		errors.assign(["Progress save missing, unreadable or too large"])
		return null
	var parser := JSON.new()
	if parser.parse(file.get_as_text()) != OK:
		errors.assign(["Progress save JSON invalid; original retained"])
		return null
	return parser.data

func write_document(document: Dictionary, path: String = PATH) -> bool:
	# Sim validates the full inventory/catalog/modifier candidate before calling.
	# This storage layer checks bounded serialization, byte readback and file IO.
	errors.clear()
	if not allowed_path(path):
		errors.assign(["Unsupported progress save path"])
		return false
	var serialized: String = JSON.stringify(document,"\t",true,true)
	if serialized.to_utf8_buffer().size() > 1048576:
		errors.assign(["Progress candidate exceeds storage size limit"])
		return false
	var absolute: String = ProjectSettings.globalize_path(path).simplify_path()
	if DirAccess.make_dir_recursive_absolute(absolute.get_base_dir()) != OK:
		errors.assign(["Cannot create progress save directory"])
		return false
	var suffix: String = "."+str(Time.get_unix_time_from_system()).replace(".","-")+"-"+str(Time.get_ticks_usec())
	var temporary: String = absolute+suffix+".pending"
	var backup: String = absolute+suffix+".previous"
	if FileAccess.file_exists(temporary) or FileAccess.file_exists(backup):
		errors.assign(["Progress save transaction name collision"])
		return false
	var file := FileAccess.open(temporary,FileAccess.WRITE)
	if file == null:
		errors.assign(["Cannot write progress candidate"])
		return false
	file.store_string(serialized)
	file.flush()
	var write_ok: bool = file.get_error() == OK
	file.close()
	if not write_ok:
		errors.assign(["Progress candidate write failed; original retained"])
		return false
	var parser := JSON.new()
	var readback: String = FileAccess.get_file_as_string(temporary)
	# JSON.parse converts integers to floats. Compare the exact written text,
	# not re-stringified variants (1 versus 1.0), while still requiring valid JSON.
	if parser.parse(readback) != OK or not parser.data is Dictionary or readback != serialized:
		errors.assign(["Progress candidate readback mismatch; original retained"])
		return false
	var had_original: bool = FileAccess.file_exists(absolute)
	var original_hash: String = FileAccess.get_sha256(absolute) if had_original else ""
	if had_original:
		if original_hash.length() != 64:
			errors.assign(["Cannot hash original progress save; default retained"])
			return false
		# copy_absolute and rename_absolute are documented static 4.5 APIs.
		# Copy first so the default path remains available until final replacement.
		if DirAccess.copy_absolute(absolute,backup) != OK or FileAccess.get_sha256(backup) != original_hash or FileAccess.get_sha256(absolute) != original_hash:
			errors.assign(["Cannot verify old progress backup; default retained"])
			return false
	if DirAccess.rename_absolute(temporary,absolute) != OK:
		if had_original and FileAccess.get_sha256(absolute) != original_hash:
			if DirAccess.copy_absolute(backup,absolute) != OK or FileAccess.get_sha256(absolute) != original_hash:
				errors.assign(["Save replacement/restore failed; verified original retained at "+backup])
			else: errors.assign(["Save replacement failed; original restored from retained backup"])
		else: errors.assign(["Save replacement failed; original/default retained"])
		return false
	# A successful replacement retains the .previous backup. No user file is deleted.
	return true
