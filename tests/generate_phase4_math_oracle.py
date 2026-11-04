"""One-time independent exact-rational fixture for the declared project rules.

No Godot/product module is imported. This is not a D2R arithmetic oracle.
"""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random

OUTPUT = Path(__file__).with_name("fixtures") / "phase4-math-oracle.json"


def clamp(value, low, high):
    return min(high, max(low, value))


def floor_fraction(numerator, denominator):
    value = Fraction(numerator, denominator)
    return value.numerator // value.denominator


def damage_case(values):
    incoming, hp, flat, resistance, power, threshold = values
    base = max(0, incoming)
    power = clamp(power, -10000, 100000)
    after_power = floor_fraction(base * (10000 + power), 10000)
    flat = max(0, flat)
    after_flat = max(0, after_power - flat)
    resistance = clamp(resistance, -10000, 10000)
    total = floor_fraction(after_flat * (10000 - resistance), 10000)
    before = max(0, hp)
    after = max(0, before - total)
    dead = after <= max(0, threshold)
    return {"input": list(values), "expected": {
        "base_raw": base, "power_bps": power, "after_power_raw": after_power,
        "flat_reduction_raw": flat, "after_flat_raw": after_flat,
        "resistance_bps": resistance, "after_resist_raw": total,
        "absorbed_damage_raw": 0, "absorb_heal_raw": 0, "total_raw": total,
        "hp_before_raw": before, "hp_after_raw": 0 if dead else after,
        "dead": dead, "death_reason": "threshold" if dead else "alive",
    }}


def main():
    if OUTPUT.exists():
        raise SystemExit("Refusing to overwrite pinned independent math oracle")
    rng = random.Random(416772)
    inputs = [
        (1536, 2304, 256, 2500, 0, 0),
        (1001, 2304, 0, 2500, 0, 0),
        (100, 1, 256, 0, 0, 0),
        (1, 256, 0, 0, 0, 0),
        (1, 1, 0, 0, 0, 0),
        (1, 256, 0, 0, 0, 255),
        (1001, 10000, 0, -10000, 0, 0),
        (1001, 10000, 0, 10000, 0, 0),
        (1, 10000, 0, 0, 5000, 0),
        (7, 10000, 1, 3333, 5000, 0),
        (-10, 256, -1, -20000, 200000, -1),
        (2147483647, 2147483647, 0, -10000, 100000, 0),
    ]
    for _ in range(180):
        inputs.append((rng.randrange(-50, 200000), rng.randrange(0, 1000000),
                       rng.randrange(-20, 3000), rng.randrange(-15000, 15001),
                       rng.randrange(-15000, 120001), rng.choice([0, 0, 0, 255])))
    costs = []
    for base in [0, 1, 7, 640, 1001, 2147483647]:
        for bps in [-10000, -9000, -1, 0, 1, 2500, 100000, 200000]:
            expected = max(1, floor_fraction(max(1, base) * (10000 + clamp(bps, -9000, 100000)), 10000))
            costs.append({"input": [base, bps], "expected": expected})
    timings = []
    for startup, cycle in [(18, 33), (12, 45), (0, 1), (18, 10), (2147483647, 2147483647)]:
        for speed in [-10000, -7500, -1, 0, 1, 30000, 100000]:
            denominator = 10000 + clamp(speed, -7500, 30000)
            start = -floor_fraction(-max(0, startup) * 10000, denominator)
            interval = -floor_fraction(-max(1, cycle) * 10000, denominator)
            timings.append({"input": [startup, cycle, speed], "expected": {"startup_ticks": start, "cycle_ticks": max(start + 1, interval)}})
    fixture = {"scope": "Independent exact Fraction arithmetic for declared phase4 project rules, not D2R",
               "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "damage": [damage_case(case) for case in inputs], "cost": costs, "timing": timings}
    OUTPUT.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"damage": len(inputs), "cost": len(costs), "timing": len(timings),
                      "sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main()
