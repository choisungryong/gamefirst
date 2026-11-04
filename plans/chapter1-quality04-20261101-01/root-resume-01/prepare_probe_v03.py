from pathlib import Path
import json,hashlib
BASE=Path(__file__).resolve().parent
source=BASE/'probe_v02.gd';dest=BASE/'probe_v03.gd';assert not dest.exists()
text=source.read_text(encoding='utf-8')
needle='func _initialize() -> void:\n';assert text.count(needle)==1
text=text.replace(needle,needle+'\tvar previous_delta:bool=OS.delta_smoothing\n\tOS.delta_smoothing=false\n\tcheck(not OS.delta_smoothing,"actual OS smoothing setter honored")\n\tOS.delta_smoothing=previous_delta\n\tcheck(OS.delta_smoothing==previous_delta,"actual OS smoothing state restored")\n')
with dest.open('x',encoding='utf-8') as f:f.write(text)
source=BASE.parent/'packaging/package_quality05.py';dest=source.with_name('package_quality06.py');assert not dest.exists()
text=source.read_text(encoding='utf-8').replace('20261101-05','20261101-06').replace("HERE/'build05'","HERE/'build06'").replace('Quality05','Quality06').replace('candidate05','candidate06')
with dest.open('x',encoding='utf-8') as f:f.write(text)
source=BASE.parent/'measurement/run_probe_candidate05.py';dest=source.with_name('run_probe_candidate06.py');assert not dest.exists()
text=source.read_text(encoding='utf-8').replace('20261101-05','20261101-06').replace("'quality05-'+run_id","'quality06-'+run_id")
with dest.open('x',encoding='utf-8') as f:f.write(text)
with (BASE/'PROBE-V03-INCIDENT.json').open('x',encoding='utf-8') as f:
    json.dump({'issue':'Candidate05 runtime OS.delta_smoothing stayed true despite launch --delta-smoothing disable; rejected0 rows retained. Optional probe now explicitly disables process-local smoothing before warmup and restores original after sampling. Normal mode untouched. All timings remain raw monotonic callback intervals; no game-resource grants.'},f,indent=2)
