extends "res://chapter1/view/chapter_hud_quality35.gd"
## Describe the new control and propagation at the growth decision itself.
func _card_description(card: Dictionary,run: RefCounted) -> String:
 var text: String=super._card_description(card,run)
 if card.kind=="passive":return text
 var effect: Dictionary=card.get("after",{})
 match String(card.get("skill_id","")):
  "chapter1.skill.ember":
   text=text.replace("처치 시 추가 효과","처치한 적에서 폭발 전파")
  "chapter1.skill.frost":
   if int(effect.get("slow_bps",0))>0:text+="\n이동속도 -%d%%"%int(effect.slow_bps/100)
   if int(effect.get("freeze_stacks",0))>0:text=text.replace("냉각 누적으로 빙결","%d회 적중 시 빙결"%int(effect.freeze_stacks))
  "chapter1.skill.arc":
   text=text.replace("처치 시 추가 효과","처치 폭발로 주변 적 타격")
   text+="\n짧은 스턴 · 일반0.3초 / 정예0.1초\n재발동 간격 · 일반2초 / 정예3초"
 return text
