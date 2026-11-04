from pathlib import Path
import hashlib,json
BASE=Path(__file__).resolve().parent
source=BASE.parent/'measurement/test_frame_probe.gd'
target=BASE/'probe_v02.gd'
assert not target.exists()
text=source.read_text(encoding='utf-8')
text=text.replace('"engine_args":["--delta-smoothing","disable"],','"engine_args":[],"delta_smoothing":false,')
text=text.replace('bad.metadata.max_fps=120','bad.metadata.delta_smoothing=true\n\tbad.metadata.max_fps=120')
text=text.replace('"explicit_delta_smoothing_disable_required"','"delta_smoothing_enabled"')
with target.open('x',encoding='utf-8') as f:f.write(text)
source=BASE.parent/'packaging/package_quality04.py'
target=source.with_name('package_quality05.py');assert not target.exists()
text=source.read_text(encoding='utf-8').replace("ID='chapter1-c2-candidate-20261101-04'","ID='chapter1-c2-candidate-20261101-05'")
text=text.replace("PROOF=HERE/'build'","PROOF=HERE/'build05'")
text=text.replace('Quality04','Quality05').replace('candidate04','candidate05')
with target.open('x',encoding='utf-8') as f:f.write(text)
source=BASE.parent/'measurement/run_probe_packaged.py'
target=source.with_name('run_probe_candidate05.py');assert not target.exists()
text=source.read_text(encoding='utf-8').replace('chapter1-c2-candidate-20261101-04','chapter1-c2-candidate-20261101-05')
text=text.replace("'quality04-'+run_id","'quality05-'+run_id")
text=text.replace("if meta['max_fps']!=0 or", "if meta.get('delta_smoothing',True):errors.append('delta_smoothing_enabled')\n    if meta['max_fps']!=0 or")
with target.open('x',encoding='utf-8') as f:f.write(text)
with (BASE/'PROBE-V02-INCIDENT.json').open('x',encoding='utf-8') as f:
    json.dump({'issue':'Candidate04 real export reported engine_args empty, so an actual correctly supplied CLI token could not satisfy guard. Formal01 rejected before sampling; its raw0 rows preserved. Use actual documented OS.delta_smoothing property; external runner retains exact movie/fixedfps-free command. Candidate05 differs only in optional QA probe logic; no combat/visual/art changes.'},f,indent=2)
