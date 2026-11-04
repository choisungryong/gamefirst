extends "res://chapter1/view/chapter_elements_quality33.gd"
## Rarity hierarchy on existing ground drops. No generation/collection changes.
const LOOT33_COLORS := {"common":Color("bcb6a8"),"magic":Color("79b9eb"),"rare":Color("e4c365"),"unique":Color("ffa653")}
var _loot33_ring: TorusMesh
func setup(owner_view: Node3D) -> void:
 super.setup(owner_view)
 _loot33_ring=TorusMesh.new();_loot33_ring.inner_radius=.22;_loot33_ring.outer_radius=.255;_loot33_ring.rings=24;_loot33_ring.ring_segments=5
func sync(run: RefCounted,delta: float) -> void:
 super.sync(run,delta)
 for item in run.items:
  if not item_nodes.has(item.uid):continue
  var root: Node3D=item_nodes[item.uid]
  if root.has_meta("rarity33_ready"):continue
  var color: Color=LOOT33_COLORS.get(item.quality,LOOT33_COLORS.common)
  var beam: MeshInstance3D=root.get_child(0)
  var shape: CylinderMesh=beam.mesh
  var height := .35;var radius := .018;var energy := .12
  match String(item.quality):
   "magic":height=.85;radius=.035;energy=.35
   "rare":height=1.5;radius=.065;energy=.75
   "unique":height=1.9;radius=.085;energy=1.0
  shape.height=height;shape.bottom_radius=radius;shape.top_radius=radius*.22
  beam.position.y=height*.5;beam.material_override=_glow(color,energy);beam.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
  var label: Label3D=root.get_child(1);label.modulate=color
  if item.quality in ["rare","unique"]:
   var ring := MeshInstance3D.new();ring.name="RareDropHalo33";ring.mesh=_loot33_ring;ring.position.y=.035;ring.material_override=_glow(color,.35);ring.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF;root.add_child(ring)
  root.set_meta("rarity33_ready",true);root.set_meta("rarity33_quality",String(item.quality))
