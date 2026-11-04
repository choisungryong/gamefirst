"""Original deterministic synthetic cues, no third-party samples or gameplay RNG.

CC0 dedication for these generated waveforms by this project. The output is an
audible implementation placeholder, not a claim of reference soundtrack quality.
"""
from pathlib import Path
import math
import random
import struct
import wave

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'expedition' / 'audio'
RATE = 22050


def render(name, duration, base, noise=0.0, sweep=0.0):
    rng = random.Random(700 + sum(map(ord, name)))
    samples = []
    phase = 0.0
    filtered = 0.0
    total = round(duration * RATE)
    for i in range(total):
        t = i / RATE
        u = t / duration
        freq = base * (1 + sweep * u)
        phase += math.tau * freq / RATE
        filtered = filtered * .9 + rng.uniform(-1, 1) * .1
        env = min(1.0, t / .012) * (1 - u) ** 2
        signal = math.sin(phase) * .5 + math.sin(phase * 1.997) * .16
        signal = (signal * (1 - noise) + filtered * noise * 3) * env * .55
        samples.append(struct.pack('<h', round(max(-1, min(1, signal)) * 32767)))
    target = OUT / (name + '.wav')
    if target.exists():
        raise RuntimeError(f'Preserve existing asset; refusing overwrite: {target}')
    with wave.open(str(target), 'wb') as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(RATE)
        writer.writeframes(b''.join(samples))


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for row in [('fire', .23, 190, .6, -0.7),
                ('cold', .38, 710, .28, .15),
                ('lightning', .22, 940, .65, -0.8),
                ('impact', .13, 110, .65, -0.7),
                ('hurt', .2, 95, .45, -0.4),
                ('death', .6, 90, .7, -0.8),
                ('drop', .32, 650, .0, -.2),
                ('pickup', .35, 880, .0, .5),
                ('equip', .18, 330, .1, .25)]:
        render(*row)
    print(f'Created 9 original mono cues in {OUT}')
