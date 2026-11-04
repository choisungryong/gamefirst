extends RefCounted
## Independent raw-integer combat. Flat reduction follows committed spell power,
## then resistance, then HP. No absorb, pierce, block, or D2R death reconstruction.
const Stats = preload("res://combat/stat_block.gd")
const MAX_RAW := 2147483647
## Public raw operands saturate to signed31bit nonnegative values before any
## multiplication. Percent operands clamp below; outputs may exceed MAX_RAW.
## This keeps every intermediate below int64 even for int64 caller inputs.

static func damage(incoming_raw: int, hp_before_raw: int, flat_reduction_raw: int = 0, resistance_bps: int = 0, power_bps: int = 0, death_threshold_raw: int = 0) -> Dictionary:
	var base: int = clampi(incoming_raw,0,MAX_RAW)
	var power: int = clampi(power_bps,-10000,100000)
	var after_power: int = Stats.floor_ratio(base*(10000+power),10000)
	var flat: int = clampi(flat_reduction_raw,0,MAX_RAW)
	var after_flat: int = maxi(0,after_power-flat)
	var resistance: int = clampi(resistance_bps,-10000,10000)
	var total: int = Stats.floor_ratio(after_flat*(10000-resistance),10000)
	var before: int = clampi(hp_before_raw,0,MAX_RAW)
	var after: int = maxi(0,before-total)
	var dead: bool = after <= clampi(death_threshold_raw,0,MAX_RAW)
	if dead: after = 0
	return {"base_raw":base,"power_bps":power,"after_power_raw":after_power,"flat_reduction_raw":flat,"after_flat_raw":after_flat,"resistance_bps":resistance,"after_resist_raw":total,"absorbed_damage_raw":0,"absorb_heal_raw":0,"total_raw":total,"hp_before_raw":before,"hp_after_raw":after,"dead":dead,"death_reason":"threshold" if dead else "alive"}

static func cost(base_raw: int, cost_bps: int) -> int:
	return maxi(1,Stats.floor_ratio(clampi(base_raw,1,MAX_RAW)*(10000+clampi(cost_bps,-9000,100000)),10000))

static func pay_cost(mana_raw: int, cost_raw: int) -> Dictionary:
	var accepted: bool = mana_raw >= 0 and mana_raw <= MAX_RAW and cost_raw > 0 and mana_raw >= cost_raw
	return {"accepted":accepted,"mana_before_raw":mana_raw,"cost_raw":cost_raw,"mana_after_raw":mana_raw-cost_raw if accepted else mana_raw}

static func timing(startup_ticks: int, cycle_ticks: int, speed_bps: int) -> Dictionary:
	var denominator: int = 10000+clampi(speed_bps,-7500,30000)
	var startup: int = -Stats.floor_ratio(-clampi(startup_ticks,0,MAX_RAW)*10000,denominator)
	var cycle: int = -Stats.floor_ratio(-clampi(cycle_ticks,1,MAX_RAW)*10000,denominator)
	return {"startup_ticks":startup,"cycle_ticks":maxi(startup+1,cycle)}
