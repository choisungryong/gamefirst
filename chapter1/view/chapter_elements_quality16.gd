extends "res://chapter1/view/chapter_elements_quality14.gd"
## Larger cold fragments now follow actual paid shatter events, including16's
## evolved direct-kill proc. No additional visual death proc or damage owner.
func setup(owner_view: Node3D) -> void:
	super.setup(owner_view)
	print("CHAPTER1_ELEMENTS16 ",JSON.stringify({"trigger":"actual shatter only","duration":.48,"damage_owner":false,"scope":"Own code geometry, not final art approval"}))
func consume(events: Array) -> void:
	var before := ice_fragments.size()
	super.consume(events)
	for i in range(before,ice_fragments.size()):
		ice_fragments[i].size*=1.35;ice_fragments[i].duration=.48
		ice_fragments[i].velocity*=1.12
