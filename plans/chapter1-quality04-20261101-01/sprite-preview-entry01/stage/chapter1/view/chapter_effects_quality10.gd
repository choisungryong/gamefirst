extends "res://chapter1/view/chapter_effects.gd"
## Short white contact strokes at actual paid hits. Cosmetic and bounded.
const CONTACT_CAP := 96
var contacts: Array[Dictionary]=[]
var contact_batch: MultiMeshInstance3D
var _contact_last_seq := -1

func setup(owner_view: Node3D) -> void:
	super.setup(owner_view)
	var quad := QuadMesh.new();quad.size=Vector2(2.2,2.2)
	contact_batch=_batch(quad,CONTACT_CAP)
	var mat := ShaderMaterial.new();mat.shader=preload("res://chapter1/view/contact_quality10.gdshader")
	contact_batch.material_override=mat

func consume(events: Array) -> void:
	var budget := 8
	for event in events:
		if int(event.seq)<=_contact_last_seq:continue
		_contact_last_seq=int(event.seq)
		if event.type!="hit" or budget<=0 or contacts.size()>=CONTACT_CAP:continue
		budget-=1
		var element := _element(event.get("skill_id",""))
		contacts.append({"at":event.position,"age":0.0,"duration":.13,"element":element,"angle":float((int(event.target_id)*37+int(event.tick)*13)%180)/180.0})
	super.consume(events)

func sync(run: RefCounted,delta: float) -> void:
	super.sync(run,delta)
	var live: Array[Dictionary]=[]
	var index := 0
	var camera := view.get_viewport().get_camera_3d()
	for hit in contacts:
		hit.age+=delta if run.mode=="playing" else 0.0
		if hit.age>=hit.duration:continue
		live.append(hit)
		var at := Vector3(hit.at.x,.95,hit.at.y)
		# Offset toward the camera just enough to sit on the struck silhouette.
		at+=camera.global_basis.z*.18
		contact_batch.multimesh.set_instance_transform(index,Transform3D(camera.global_basis,at))
		contact_batch.multimesh.set_instance_custom_data(index,Color(hit.age/hit.duration,hit.element,hit.angle,1))
		index+=1
	contacts=live;contact_batch.multimesh.visible_instance_count=index

func reset() -> void:
	super.reset();contacts.clear();_contact_last_seq=-1
	if contact_batch:contact_batch.multimesh.visible_instance_count=0
