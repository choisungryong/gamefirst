"""Launch isolated native QA and wait for actual OS close, never inject UI."""
from pathlib import Path
import argparse,hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def emit(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args()
    out=Path(args.output).resolve()
    if out.exists() or not out.is_relative_to(ROOT/'evidence/phase7'):raise RuntimeError('Use new bounded native output')
    out.mkdir(parents=True)
    record=ROOT/'evidence/phase7/builds/phase7-candidate-20261030-01/build.json'
    build=json.loads(record.read_text(encoding='utf-8-sig'))
    manifest=json.loads(Path(build['source_manifest']).read_text(encoding='utf-8-sig'))
    assert all(sha(ROOT/p)==h for p,h in manifest.items())
    assert sha(build['exe'])==build['exe_sha256']
    script=ROOT/'tests/phase7_native_runtime.gd'
    (out/'external-harness.gd').write_bytes(script.read_bytes())
    user=Path.home()/'AppData/Roaming/Godot/app_userdata/D2R Combat Baseline'
    guards={str(user/n):sha(user/n) if (user/n).is_file() else None for n in ['equipment-v1.json','progress-v1.json']}
    command=[build['exe'],'--windowed','--resolution','1440x810','--script',str(script),'--',f'--native-output={(out/"case").as_posix()}',f'--expected-metadata={build["metadata_sha256"]}']
    with (out/'stdout.log').open('wb') as stdout,(out/'stderr.log').open('wb') as stderr:
        process=subprocess.Popen(command,cwd=str(Path(build['exe']).parent),stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
        emit(out/'launch.json',{'pid':process.pid,'command':command,'build_record':str(record),'exe_sha256':build['exe_sha256'],'metadata_sha256':build['metadata_sha256'],'external_script_sha256':sha(script),'native_guards_before':guards})
        try:code=process.wait(timeout=900)
        except subprocess.TimeoutExpired:process.kill();raise
    after={p:sha(p) if Path(p).is_file() else None for p in guards}
    receipt={'actual_exit':code,'native_guards_unchanged':after==guards,'native_guards_after':after,'source_mismatches':[p for p,h in manifest.items() if sha(ROOT/p)!=h],'exe_sha256':sha(build['exe']),'harness_matches':sha(script)==sha(out/'external-harness.gd'),'stderr_bytes':(out/'stderr.log').stat().st_size}
    emit(out/'receipt.json',receipt);print(json.dumps(receipt))
    raise SystemExit(0 if code==0 and after==guards and not receipt['source_mismatches'] and receipt['harness_matches'] else 1)
if __name__=='__main__':main()
