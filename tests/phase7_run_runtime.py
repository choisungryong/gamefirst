"""Serial external candidate QA with immutable launch/harness receipts."""
from pathlib import Path
import argparse,csv,hashlib,json,subprocess,time,ctypes
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def emit(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',default='features',choices=['features','pilot','stress','soak'])
    ap.add_argument('--seconds',type=float,default=310)
    ap.add_argument('--warmup',type=float,default=0)
    ap.add_argument('--width',type=int,default=1920)
    ap.add_argument('--height',type=int,default=1080)
    ap.add_argument('--harness',default='phase7_runtime_gpu.gd')
    ap.add_argument('--output',required=True)
    args=ap.parse_args()
    out=Path(args.output).resolve()
    if out.exists() or not out.is_relative_to(ROOT/'evidence/phase7'): raise RuntimeError('Use new bounded evidence output')
    out.mkdir(parents=True)
    record=ROOT/'evidence/phase7/builds/phase7-candidate-20261030-01/build.json'
    build=json.loads(record.read_text(encoding='utf-8-sig'))
    manifest=json.loads(Path(build['source_manifest']).read_text(encoding='utf-8-sig'))
    assert all(sha(ROOT/p)==h for p,h in manifest.items()),'Frozen original product changed'
    assert sha(build['exe'])==build['exe_sha256']
    script=(ROOT/'tests'/args.harness).resolve()
    assert script.is_relative_to(ROOT/'tests') and script.suffix=='.gd'
    (out/'external-harness.gd').write_bytes(script.read_bytes())
    # Godot itself creates a fresh child output; launcher receipts remain outside.
    case=out/'case'
    command=[build['exe'],'--windowed','--resolution',f'{args.width}x{args.height}','--rendering-method','forward_plus','--rendering-driver','vulkan','--script',str(script),'--',f'--qa-output={case.as_posix()}',f'--expected-metadata={build["metadata_sha256"]}',f'--qa-mode={args.mode}',f'--qa-seconds={args.seconds}',f'--qa-warmup={args.warmup}',f'--qa-width={args.width}',f'--qa-height={args.height}']
    user=Path.home()/'AppData/Roaming/Godot/app_userdata/D2R Combat Baseline'
    guards={str(user/n):sha(user/n) if (user/n).is_file() else None for n in ['equipment-v1.json','progress-v1.json']}
    emit(out/'launch.json',{'command':command,'build_record':str(record),'exe_sha256':build['exe_sha256'],'metadata_sha256':build['metadata_sha256'],'external_script_sha256':sha(script),'native_guards_before':guards,'scope':'Automated external SceneTree candidate; not OS input'})
    class Counters(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong),('PeakWorkingSetSize',ctypes.c_size_t),('WorkingSetSize',ctypes.c_size_t),('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t),('PrivateUsage',ctypes.c_size_t)]
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.restype=ctypes.c_void_p
    kernel.CloseHandle.argtypes=[ctypes.c_void_p]
    psapi=ctypes.WinDLL('psapi',use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong]
    started=time.monotonic()
    with (out/'stdout.log').open('wb') as stdout,(out/'stderr.log').open('wb') as stderr,(out/'process-memory.csv').open('w',newline='') as mf:
        process=subprocess.Popen(command,cwd=str(Path(build['exe']).parent),stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
        handle=kernel.OpenProcess(0x410,False,process.pid)
        writer=csv.writer(mf);writer.writerow(['elapsed_seconds','private_bytes','working_set_bytes'])
        try:
            while process.poll() is None:
                counter=Counters();counter.cb=ctypes.sizeof(counter)
                if handle and psapi.GetProcessMemoryInfo(handle,ctypes.byref(counter),counter.cb):
                    writer.writerow([time.monotonic()-started,counter.PrivateUsage,counter.WorkingSetSize]);mf.flush()
                if time.monotonic()-started>args.seconds+args.warmup+90:
                    process.kill();raise TimeoutError('Owned candidate QA deadline')
                time.sleep(.5)
        finally:
            if handle:kernel.CloseHandle(handle)
    summary=json.loads((case/'summary.json').read_text(encoding='utf-8')) if (case/'summary.json').is_file() else None
    after={p:sha(p) if Path(p).is_file() else None for p in guards}
    receipt={'actual_exit':process.returncode,'wall_seconds':time.monotonic()-started,'report_success':bool(summary and summary['success']),'native_guards_unchanged':after==guards,'native_guards_after':after,'source_mismatches':[p for p,h in manifest.items() if sha(ROOT/p)!=h],'exe_sha256':sha(build['exe']),'external_harness_matches':sha(script)==sha(out/'external-harness.gd'),'stderr_bytes':(out/'stderr.log').stat().st_size}
    emit(out/'receipt.json',receipt)
    print(json.dumps(receipt,ensure_ascii=False))
    raise SystemExit(0 if process.returncode==0 and receipt['report_success'] and receipt['native_guards_unchanged'] and not receipt['source_mismatches'] and receipt['external_harness_matches'] else 1)
if __name__=='__main__': main()
