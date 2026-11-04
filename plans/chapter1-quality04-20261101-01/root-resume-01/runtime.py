from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,data):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
mode,run_id=sys.argv[1:3]
assert mode in ('preview','native') and run_id.replace('-','').isalnum()
build=json.loads((BASE.parent/'packaging/build/build.json').read_text(encoding='utf-8'))
exe=Path(build['exe']);assert sha(exe)==build['sha256']
proof=BASE/run_id;capture=exe.parent/'qa-captures'/run_id
assert not proof.exists() and not capture.exists()
proof.mkdir()
command=[str(exe),'--resolution','1920x1080' if mode=='preview' else '1440x810','--log-file',str(proof/'godot.log'),'--','--chapter1-capture-dir='+str(capture)]
if mode=='preview':command+=['--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-quit-after=90']
pins=json.loads((BASE.parent/'packaging/build/source-manifest.json').read_text(encoding='utf-8'))
assert all(sha(ROOT/p)==h for p,h in pins.items())
started=time.time()
with (proof/'stdout.log').open('xb') as out,(proof/'stderr.log').open('xb') as err:
    process=subprocess.Popen(command,cwd=exe.parent,stdout=out,stderr=err)
    write(proof/'LAUNCH.json',{'command':command,'pid':process.pid,'started_unix':started,'exe_sha256':sha(exe),'mode':mode,'scope':'GPU preview with normal pilot/ignore-focus; not formal performance or manual play' if mode=='preview' else 'Root native input session; individual observations determine coverage'})
    print(json.dumps({'pid':process.pid,'proof':str(proof)}),flush=True)
    code=process.wait()
copied={}
if capture.exists():
    for source in sorted(capture.glob('*.png')):
        target=proof/'captures'/source.name;target.parent.mkdir(exist_ok=True)
        assert not target.exists();shutil.copy2(source,target);assert sha(source)==sha(target)
        copied[source.name]=sha(target)
raw=(proof/'stdout.log').read_text(encoding='utf-8',errors='replace')
results=[json.loads(line.split('CHAPTER1_RUNTIME_RESULT ',1)[1]) for line in raw.splitlines() if 'CHAPTER1_RUNTIME_RESULT ' in line]
write(proof/'EXECUTION.json',{'actual_exit':code,'wall_seconds':time.time()-started,'exe_unchanged':sha(exe)==build['sha256'],'source_mismatches':[p for p,h in pins.items() if sha(ROOT/p)!=h],'captures':copied,'results':results,'stderr_bytes':(proof/'stderr.log').stat().st_size})
print(json.dumps({'actual_exit':code,'captures':len(copied),'proof':str(proof),'results':results},ensure_ascii=False))
