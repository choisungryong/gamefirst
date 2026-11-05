extends "res://chapter1/view/chapter_elements_quality33b.gd"
## Bounded shock cues follow actual living stunned enemies, never a second timer.
const STUN36_VISIBLE_CAP := 48
var _stun36_sparks: MultiMeshInstance3D
var stun36_visible := 0
func setup(owner_view: Node3D) -> void:
 super.setup(owner_view)
 _stun36_sparks=MultiMeshInstance3D.new();_stun36_sparks.name="ShockOrbit36"
 var geometry := SphereMesh.new();geometry.radius=.045;geometry.height=.09;geometry.radial_segments=8;geometry.rings=4
 var batch := MultiMesh.new();batch.transform_format=MultiMesh.TRANSFORM_3D;batch.mesh=geometry;batch.instance_count=STUN36_VISIBLE_CAP*3;batch.visible_instance_count=0
 _stun36_sparks.multimesh=batch;_stun36_sparks.material_override=_glow(Color("f5d878"),1.5);_stun36_sparks.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
 view.add_child(_stun36_sparks)
func sync(run: RefCounted,delta: float) -> void:
 super.sync(run,delta)
 stun36_visible=0
 var ids: Array=run.enemies.keys();ids.sort()
 for id_ in ids:
  var entity: Dictionary=run.enemies[id_]
  if entity.hp_raw<=0 or run.tick>=int(entity.get("stunned_until",0)):continue
  if stun36_visible>=STUN36_VISIBLE_CAP:break
  var height: float=2.1 if entity.elite else 1.5
  for point in 3:
   var angle: float=float(run.tick)*.22+TAU*float(point)/3.0
   var position := Vector3(entity.position.x+cos(angle)*.28,height+sin(angle*2.0)*.08,entity.position.y+sin(angle)*.28)
   _stun36_sparks.multimesh.set_instance_transform(stun36_visible*3+point,Transform3D(Basis.IDENTITY,position))
  stun36_visible+=1
 _stun36_sparks.multimesh.visible_instance_count=stun36_visible*3
func reset() -> void:
 super.reset();stun36_visible=0
 if is_instance_valid(_stun36_sparks):_stun36_sparks.multimesh.visible_instance_count=0

func consume(events: Array) -> void:
 var previous_seq: int=_element_seq
 var previous_links: int=arc_links.size()
 super.consume(events)
 var casts: Array=[]
 for event in events:
  if int(event.seq)>previous_seq and event.type=="cast" and event.get("skill_id","")=="chapter1.skill.arc":
   if not event.has("segments"):return
   casts.append(event)
 if casts.is_empty():return
 # Remove only the newly appended legacy concatenated paths; keep older fading arcs.
 arc_links.resize(previous_links)
 for event in casts:
  for segment in event.segments:
   if arc_links.size()>=ARC_CAP:break
   arc_links.append({"from":segment.from,"to":segment.to,"age":0.0,"duration":.20,"evolved":bool(event.get("evolved",false)),"seed":int(event.seq)*17+arc_links.size()*13})
