from pathlib import Path
import array, hashlib, json, math, sys, wave

base = Path('C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/full26/audio')
output = base / 'SIGNAL-REVIEW01.json'
assert not output.exists()
rows = []
for name in ['ember01', 'frost01', 'arc01']:
    folder = base / name
    result = json.loads((folder / 'proof/RESULT.json').read_text(encoding='utf-8'))
    execution = json.loads((folder / 'gpu-execution.json').read_text())
    path = folder / 'proof/actual-game-mix.wav'
    with wave.open(str(path), 'rb') as wav:
        channels, width, rate, frames = wav.getnchannels(), wav.getsampwidth(), wav.getframerate(), wav.getnframes()
        assert width == 2
        samples = array.array('h', wav.readframes(frames))
    if sys.byteorder != 'little':
        samples.byteswap()
    rms = math.sqrt(sum(float(x)*x for x in samples) / len(samples))
    rows.append(dict(run=name, primary=result['primary'], duration_seconds=frames/rate,
        channels=channels, sample_width_bytes=width, sample_rate=rate,
        peak_abs=max(abs(x) for x in samples), rms=rms,
        rms_dbfs=20*math.log10(rms/32768) if rms else None,
        full_scale_samples=sum(x in (-32768,32767) for x in samples),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        start_tick=result['start_tick'], final_tick=result['final_tick'],
        played=result['played'], dropped=result['dropped'],
        same_complete_core=result['same_complete_core'], execution=execution))
    assert execution == {'exit':0,'stderr_bytes':0} and result['same_complete_core']
document = dict(runs=rows,
    raw_metadata_correction='RESULT.json cue_counts is cyclic variant-index delta, NOT per-cue playback counts. Raw files remain untouched. played/dropped are monotonic totals.',
    scope='Actual candidate26 Master bus at normal earned checkpoint, all learned skills active. Signal statistics do not establish hearing, balance, speaker level, manual play, full chapter or formal performance approval.')
output.write_text(json.dumps(document,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(document,ensure_ascii=False,indent=2))
