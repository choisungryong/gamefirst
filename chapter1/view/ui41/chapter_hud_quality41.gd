extends "res://chapter1/view/ui40/chapter_hud_quality40.gd"
## Menu-only portrait successor. The inherited start/stash callbacks stay on
## their existing controls. This 2D concept does not replace the 3D actor.
const OathPortrait41=preload("res://chapter1/art/portrait41/oath_witch_portrait_v01.png")

func _build_modal(run: RefCounted) -> void:
	super._build_modal(run)
	if run.mode!="menu" or stash_open or not overlay.visible:return
	var original := modal.get_child(0) as VBoxContainer
	if original==null or original.get_child_count()<7:return
	var inherited_starts := original.get_child(3) as HBoxContainer
	if inherited_starts==null or inherited_starts.get_child_count()!=3:return
	_build_menu41(original,inherited_starts)
	_focus_modal38.call_deferred()

func _build_menu41(original: VBoxContainer,inherited_starts: HBoxContainer) -> void:
	# Keep the exact three inherited skill-id closures and the real profile
	# footer. Reparenting changes presentation, not the start/save contract.
	var title := original.get_child(0) as Label
	var description := original.get_child(1) as Label
	var controls := original.get_child(2) as Label
	var old_spacer := original.get_child(4)
	var motion := original.get_child(5) as CheckButton
	var scope := original.get_child(6) as Label
	if title==null or description==null or controls==null or motion==null or scope==null:return
	var starts: Array[Node]=inherited_starts.get_children()
	for child in starts:
		if not child is Button:return
	var original_children: Array[Node]=original.get_children()
	modal.remove_child(original)
	var row := HBoxContainer.new();row.name="OathMenu41"
	row.add_theme_constant_override("separation",34);modal.add_child(row)
	var portrait_frame := PanelContainer.new();portrait_frame.name="OathPortrait41"
	portrait_frame.size_flags_vertical=Control.SIZE_SHRINK_CENTER
	var portrait_style := _style(Color("111416"),Color("665c46"))
	portrait_style.set_content_margin_all(12);portrait_style.border_width_top=1
	portrait_frame.add_theme_stylebox_override("panel",portrait_style);row.add_child(portrait_frame)
	var portrait := TextureRect.new();portrait.name="PortraitTexture41"
	portrait.texture=OathPortrait41;portrait.custom_minimum_size=Vector2(360,540)
	# Official4.5 TextureRect: IGNORE_SIZE permits the source1024x1536 to
	# shrink; KEEP_ASPECT_CENTERED shows the whole portrait without distortion.
	# https://docs.godotengine.org/en/4.5/classes/class_texturerect.html
	portrait.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
	portrait.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	portrait.mouse_filter=Control.MOUSE_FILTER_IGNORE;portrait_frame.add_child(portrait)
	var body := VBoxContainer.new();body.name="StartChoices41"
	body.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	body.add_theme_constant_override("separation",12);row.add_child(body)
	title.reparent(body);title.add_theme_font_size_override("font_size",40)
	title.add_theme_color_override("font_color",Color("e8d5a6"))
	description.reparent(body);description.add_theme_font_size_override("font_size",19)
	description.add_theme_color_override("font_color",Color("d0c7b6"))
	controls.reparent(body);controls.add_theme_font_size_override("font_size",15)
	controls.add_theme_color_override("font_color",Color("aeb5ab"))
	body.add_child(_label("첫 기술을 선택하세요",17,Color("aa8d58")))
	var choices := VBoxContainer.new();choices.name="PrimarySkillChoices41"
	choices.add_theme_constant_override("separation",8);body.add_child(choices)
	var tints := [Color("e8a05a"),Color("7cc9d9"),Color("abb8ec")]
	# Rank1 base definitions: growth_quality37.json. Gear can modify these
	# later; rank1 frost slows but has freeze_stacks=0, so no freeze claim.
	var summaries := ["기본 피해 12 · 화염탄 1발","기본 피해 10 · 관통 2회 · 적 이동 속도 -20%","기본 피해 9 · 3대상 연쇄 · 짧은 기절"]
	for i in starts.size():
		var button := starts[i] as Button
		button.reparent(choices);button.custom_minimum_size.y=88
		button.text+="\n"+summaries[i]
		button.size_flags_horizontal=Control.SIZE_EXPAND_FILL
		button.add_theme_font_size_override("font_size",20)
		button.add_theme_color_override("font_color",tints[i])
	var space := Control.new();space.size_flags_vertical=Control.SIZE_EXPAND_FILL;body.add_child(space)
	var preferences := HBoxContainer.new();preferences.add_theme_constant_override("separation",20)
	body.add_child(preferences);motion.reparent(preferences)
	motion.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	preferences.add_child(_button("음소거 전환 [M]",func():mute_toggle.emit()))
	# Stash button, actual profile note, and any inherited production note keep
	# their original order and callbacks. The old layout spacer is discarded.
	for child in original_children:
		if child in [title,description,controls,inherited_starts,old_spacer,motion,scope]:continue
		child.reparent(body)
	scope.reparent(body);scope.add_theme_font_size_override("font_size",14)
	scope.add_theme_color_override("font_color",Color("97988e"))
	original.queue_free()
	modal.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	modal.offset_left=-680;modal.offset_right=680
	modal.offset_top=-350;modal.offset_bottom=350
