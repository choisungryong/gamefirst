"""Read-only CSV/PNG/identity audit for the short stationary ground32 probe."""
from pathlib import Path
import csv, hashlib, json, math, struct, sys

ROOT=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def audit(directory):
    errors=[]
    def require(ok,msg):
        if not ok: errors.append(msg)
    build=read(ROOT/'evidence/phase6/builds/phase6-candidate-20261030-01/build.json')
    summary=read(directory/'summary.json')
    launch=read(Path(str(directory)+'.launch.json'))
    receipt=read(Path(str(directory)+'.receipt.json'))
    rows=list(csv.DictReader((directory/'frames.csv').open(encoding='utf-8-sig',newline='')))
    elapsed=[float(r['elapsed_seconds']) for r in rows]
    times=[float(r['frame_ms']) for r in rows]
    ordered=sorted(times)
    p95=ordered[math.ceil(len(ordered)*.95)-1]
    require(all(math.isfinite(x) and x>0 for x in elapsed+times),'Finite positive timings')
    require(all(b>a for a,b in zip(elapsed,elapsed[1:])),'Strict timestamp order')
    require(elapsed[0]>=2 and 7.9<=elapsed[-1]-elapsed[0]<=8.1,'Warmup and diagnostic sample span')
    require(all(abs((elapsed[i]-elapsed[i-1])*1000-times[i])<.0021 for i in range(1,len(rows))),'Frame durations agree with timestamp intervals')
    require(all(int(r['marker_count'])==int(r['ground_count'])==32 for r in rows),'Stationary32 ground/markers every row')
    nodes=[int(r['node_count']) for r in rows]
    require(min(nodes)==max(nodes)==summary['node_min']==summary['node_max']==219,'Stable219 nodes')
    require(summary['success'] is True and summary['failures']==[],'Probe reported success')
    require(summary['sample_count']==len(rows) and abs(summary['sample_seconds']-(elapsed[-1]-elapsed[0]))<.000002,'Summary sample count/span')
    require(abs(summary['frame_ms']['p95']-p95)<.000001 and abs(summary['frame_ms']['worst']-max(times))<.000001,'Summary p95/worst agree with raw CSV')
    require(summary['metadata_sha256']==build['metadata_sha256'],'Embedded metadata identity')
    require(summary['renderer']=='forward_plus','Renderer identity')
    require(Path(summary['executable']).resolve()==Path(build['exe']).resolve(),'Runtime executable identity')
    require(sha(Path(build['exe']))==build['exe_sha256']==launch['exe_sha256']==receipt['exe_sha256'],'EXE bytes/launch/receipt')
    require(summary['external_script_sha256']==launch['script_sha256']==sha(directory/'external-harness.gd')==sha(ROOT/'tests/phase6_loot_gpu_probe.gd'),'Current and preserved harness identity')
    require(receipt['actual_exit']==0 and receipt['stderr_bytes']==0 and receipt['remaining']==0,'Actual exit/stderr/process receipt')
    blob=(directory/'frame-ground32.png').read_bytes()
    require(blob[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',blob[16:24])==(1920,1080)==tuple(summary['framebuffer']),'Actual framebuffer PNG')
    return {'scope':'Stationary ground32 short diagnostic only: no timed enemies/deaths, no formal60s/300enemy/fixed60FPS claim; physics stepping is in preserved harness, not independently timestamped in CSV','success':not errors,'failures':errors,'sample_count':len(rows),'sample_seconds':elapsed[-1]-elapsed[0],'p50_ms':ordered[math.ceil(len(ordered)*.5)-1],'p95_ms':p95,'p99_ms':ordered[math.ceil(len(ordered)*.99)-1],'worst_ms':max(times),'node_min':min(nodes),'node_max':max(nodes),'png_sha256':sha(directory/'frame-ground32.png'),'csv_sha256':sha(directory/'frames.csv')}

if __name__=='__main__':
    result=audit(Path(sys.argv[1]))
    if len(sys.argv)>2:
        path=Path(sys.argv[2])
        if path.exists(): raise RuntimeError('Preserve previous audit')
        path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))
    raise SystemExit(0 if result['success'] else 1)
