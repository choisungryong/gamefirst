"""Original quiet wind loop, synthesized without samples. CC0 project dedication."""
from pathlib import Path
import math
import random
import struct
import wave

target = Path(__file__).resolve().parents[1] / 'assets/expedition/audio/ambience.wav'
if target.exists():
    raise RuntimeError('Preserve existing ambience; do not overwrite')
rate = 22050
duration = 4
rng = random.Random(7171)
filtered = 0.0
samples = []
for i in range(rate * duration):
    t = i / rate
    filtered = filtered * .985 + rng.uniform(-1, 1) * .015
    # Integer-cycle oscillators and an end taper keep the seam quiet.
    taper = min(1, t / .15, (duration - t) / .15)
    signal = (filtered * .18 + math.sin(math.tau * 48 * t) * .006
              + math.sin(math.tau * 72 * t) * .003) * taper
    samples.append(struct.pack('<h', round(signal * 32767)))
with wave.open(str(target), 'wb') as writer:
    writer.setnchannels(1)
    writer.setsampwidth(2)
    writer.setframerate(rate)
    writer.writeframes(b''.join(samples))
print(target)
