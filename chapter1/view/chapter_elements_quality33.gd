extends "res://chapter1/view/chapter_elements_quality26.gd"
## Preserve paid fire impacts; keep billboard heat below the upper-body silhouette.
func setup(owner_view: Node3D) -> void:
 super.setup(owner_view)
 var material := ShaderMaterial.new()
 material.shader=preload("res://chapter1/view/flame_bloom_quality33.gdshader")
 plumes.material_override=material
func sync(run: RefCounted,delta: float) -> void:
 super.sync(run,delta)
 for index in plumes.multimesh.visible_instance_count:
  var transform := plumes.multimesh.get_instance_transform(index)
  transform.basis=transform.basis.scaled(Vector3(.85,.52,.85))
  transform.origin.y*=.52
  plumes.multimesh.set_instance_transform(index,transform)
