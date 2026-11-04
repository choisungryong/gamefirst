extends RefCounted
## Independent cumulative XP design; levels only unlock equipment requirements.
const MAX_XP := 1000000000
const XP_PER_KILL := 3
var xp := 0
func level() -> int:
	return 3 if xp >= 18 else (2 if xp >= 6 else 1)
func award() -> int:
	var before := xp
	xp = mini(MAX_XP,xp+XP_PER_KILL)
	return xp-before
func snapshot() -> Dictionary:
	return {"xp":xp,"level":level(),"next_level_xp":6 if xp < 6 else (18 if xp < 18 else 0)}

