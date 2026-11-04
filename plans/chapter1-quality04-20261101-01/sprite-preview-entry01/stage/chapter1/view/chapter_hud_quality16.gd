extends "res://chapter1/view/chapter_hud.gd"
func _card_description(card: Dictionary,run: RefCounted) -> String:
	var text := super._card_description(card,run)
	if card.get("skill_id","")=="chapter1.skill.frost":
		var effect: Dictionary=card.get("after",{})
		if int(effect.get("shatter_count",0))>0 and int(effect.get("radius_cm",0))>0:
			text=text.replace("범위 %.1fm"%(float(effect.radius_cm)/100),"파쇄3.5m · 최대%d대상"%int(effect.shatter_count))
		if card.get("kind","")=="evolve":text=text.replace("빙결된 적 처치 시 파쇄","냉기 처치 시 파쇄\n파편50% · 정예25%")
	return text
