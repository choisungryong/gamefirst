extends RefCounted
## New product profile only. Old Baseline saves are neither read nor migrated.
const Items=preload("res://chapter1/core/chapter_items.gd")
const Catalog=preload("res://chapter1/core/growth_catalog.gd")
const CAPACITY := 256
const MAX_ITEMS := 325 # One final69-item recovery batch; start blocked above256.
var state: Dictionary={}
var error := ""
var path := ""
var _loaded_text := ""
var available := false

static func fresh() -> Dictionary:
	return {"schema_version":1,"revision":0,"next_id":1,"items":[],"equipped":{},"completed_runs":0,"best_ticks":0,"essence":0,"receipts":[]}

func configure(destination: String="user://chapter-one-profile-v1.json",qa: bool=false) -> bool:
	available=false;error="";state=fresh();path=destination;_loaded_text=""
	if qa:
		var base := "res://plans/chapter1-quality04-20261101-01/"
		if not path.begins_with(base) or not path.ends_with(".json"):error="Invalid isolated QA profile path";return false
	else:
		if destination!="user://chapter-one-profile-v1.json" or not ProjectSettings.get_setting("application/config/use_custom_user_dir",false) or not String(ProjectSettings.get_setting("application/config/custom_user_dir_name","")).begins_with("AshenCloisterChapterOne"):
			error="전용 저장 경로가 없는 미리보기입니다";return false
	if FileAccess.file_exists(path):
		_loaded_text=FileAccess.get_file_as_string(path)
		if _loaded_text.length()>2000000:error="Profile exceeds bound";return false
		var parser := JSON.new()
		if parser.parse(_loaded_text)!=OK:error="저장 파일 검증 실패 · 원본 보존";return false
		var normalized := normalize(parser.data)
		if normalized.is_empty():error="저장 파일 검증 실패 · 원본 보존";return false
		state=normalized
	available=true;return true

static func normalize(value: Variant) -> Dictionary:
	if not value is Dictionary or not Catalog.keys_match(value,["schema_version","revision","next_id","items","equipped","completed_runs","best_ticks","essence","receipts"]):return {}
	for key in ["schema_version","revision","next_id","completed_runs","best_ticks","essence"]:
		if not Catalog.integer(value[key],0,1000000000):return {}
	if value.schema_version!=1 or value.next_id<1 or not value.items is Array or value.items.size()>MAX_ITEMS or not value.equipped is Dictionary or value.equipped.size()>4 or not value.receipts is Array or value.receipts.size()>64:return {}
	var result: Dictionary=value.duplicate(true)
	for key in ["schema_version","revision","next_id","completed_runs","best_ticks","essence"]:result[key]=int(result[key])
	var ids := {};var slots := {}
	for record in result.items:
		if not record is Dictionary or not Catalog.keys_match(record,["storage_id","item"]) or not Catalog.integer(record.storage_id,1,999999999) or ids.has(int(record.storage_id)) or record.storage_id>=result.next_id:return {}
		record.storage_id=int(record.storage_id)
		var item: Variant=record.item
		if not item is Dictionary or not Catalog.keys_match(item,["base_id","name","slot","stats","quality","item_level","affixes","description"]) or not item.stats is Dictionary or not item.affixes is Array:return {}
		if not item.name is String or item.name.length()>160 or not item.base_id is String or item.base_id.length()>100 or not item.description is String or item.description.length()>300:return {}
		if not Catalog.integer(item.item_level,1,12):return {}
		item.item_level=int(item.item_level)
		for stat in item.stats:
			if not Catalog.integer(item.stats[stat],-1000000,1000000):return {}
			item.stats[stat]=int(item.stats[stat])
		for affix in item.affixes:
			if not affix is Dictionary or not Catalog.keys_match(affix,["id","group","stat","value"]) or not Catalog.integer(affix.value,0,1000000):return {}
			affix.value=int(affix.value)
		if not Items.validate(item).is_empty():return {}
		ids[record.storage_id]=true;slots[record.storage_id]=item.slot
	for slot in result.equipped:
		if not slot in ["weapon","body","charm","ring"] or not Catalog.integer(result.equipped[slot],1,999999999):return {}
		var id_ := int(result.equipped[slot])
		if not ids.has(id_) or slots[id_]!=slot:return {}
		result.equipped[slot]=id_
	for receipt in result.receipts:
		if not receipt is String or receipt.length()<1 or receipt.length()>120:return {}
	return result

func _persist(candidate: Dictionary) -> bool:
	if not available:error="저장 경로 검증이 필요합니다";return false
	candidate=candidate.duplicate(true);candidate.revision=int(state.revision)+1
	var normalized := normalize(candidate)
	if normalized.is_empty():error="저장 후보 검증 실패";return false
	if FileAccess.file_exists(path):
		if FileAccess.get_file_as_string(path)!=_loaded_text:error="다른 실행에서 저장이 변경됐습니다 · 기존 파일 보존";return false
	elif not _loaded_text.is_empty():error="저장 파일이 외부에서 이동됐습니다";return false
	var text := JSON.stringify(normalized,"  ")
	var stamp := "%06d-%d-%d"%[normalized.revision,OS.get_process_id(),Time.get_ticks_usec()]
	var journal := path.get_basename()+".revision-"+stamp+".json"
	var temporary := path.get_basename()+".next-"+stamp+".json"
	if FileAccess.file_exists(journal) or FileAccess.file_exists(temporary):error="저장 파일 이름 충돌";return false
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	for target in [journal,temporary]:
		var file := FileAccess.open(target,FileAccess.WRITE)
		if file==null:error="저장 파일 생성 실패";return false
		file.store_string(text);file.flush();var status := file.get_error();file.close()
		if status!=OK or FileAccess.get_file_as_string(target)!=text:error="저장 쓰기 검증 실패";return false
	# The immutable revision remains if replacement fails. No historic backup is deleted.
	var rename := DirAccess.rename_absolute(temporary,path)
	if rename!=OK:error="저장 교체 실패 · 이전 파일과 새 revision 보존";return false
	if FileAccess.get_file_as_string(path)!=text:error="저장 교체 검증 실패";return false
	state=normalized;_loaded_text=text;error="";return true

func record_run(receipt: String,inventory: Array,pending: Array,victory: bool,ticks: int) -> bool:
	if not available:return false
	if receipt in state.receipts:return true
	if receipt.length()<1 or receipt.length()>120 or inventory.size()>65 or pending.size()>4 or ticks<0:return false
	var candidate: Dictionary=state.duplicate(true)
	for source in inventory+pending:
		if source.has("storage_id"):continue
		if not Items.validate(source).is_empty():error="보상 장비 검증 실패";return false
		var clean := {}
		for key in ["base_id","name","slot","stats","quality","item_level","affixes","description"]:clean[key]=source[key]
		candidate.items.append({"storage_id":int(candidate.next_id),"item":clean.duplicate(true)});candidate.next_id+=1
	if candidate.items.size()>MAX_ITEMS:error="장비 보관 공간이 부족합니다";return false
	candidate.receipts.append(receipt)
	if candidate.receipts.size()>64:candidate.receipts.pop_front()
	if victory:
		candidate.completed_runs+=1
		if candidate.best_ticks==0 or ticks<candidate.best_ticks:candidate.best_ticks=ticks
	return _persist(candidate)

func select_item(storage_id: int) -> bool:
	var candidate: Dictionary=state.duplicate(true)
	for record in candidate.items:
		if record.storage_id==storage_id:candidate.equipped[record.item.slot]=storage_id;return _persist(candidate)
	return false

func salvage(storage_id: int) -> bool:
	var candidate: Dictionary=state.duplicate(true);var index := -1
	for i in candidate.items.size():
		if candidate.items[i].storage_id==storage_id:index=i;break
	if index<0:return false
	var item: Dictionary=candidate.items[index].item
	if candidate.equipped.get(item.slot,-1)==storage_id:candidate.equipped.erase(item.slot)
	candidate.items.remove_at(index);candidate.essence=mini(1000000000,int(candidate.essence)+({"common":1,"magic":3,"rare":8,"unique":25}.get(item.quality,1)))
	return _persist(candidate)

func starting_gear() -> Array[Dictionary]:
	var result: Array[Dictionary]=[]
	for record in state.get("items",[]):
		if state.equipped.get(record.item.slot,-1)==record.storage_id:
			var item: Dictionary=record.item.duplicate(true);item.storage_id=record.storage_id;result.append(item)
	return result
