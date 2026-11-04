from pathlib import Path
import json,subprocess,hashlib,shutil
ROOT=Path('C:/Project/d2r-combat-baseline');BASE=ROOT/'plans/chapter1-quality04-20261101-01';HERE=Path(__file__).parent
OUT=BASE/'full16/runtime/gpu-cold01'
assert not OUT.exists();OUT.mkdir(parents=True)
build=json.loads((BASE/'full16/build/build.json').read_text(encoding='utf-8'));exe=Path(build['exe'])
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(exe)==build['sha256']
capture=exe.parent/'qa-captures/gpu-cold01';assert not capture.exists()
script=HERE/'packaged_gpu16.gd'
cmd=[str(exe),'--script',str(script),'--max-fps','120','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-primary=chapter1.skill.frost','--chapter1-seed=90131','--chapter1-qa-ignore-focus','--chapter1-capture-dir='+str(capture),'--chapter1-quit-after=450']
def write(p,v):
    assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
with(OUT/'stdout.txt').open('xb') as o,(OUT/'stderr.txt').open('xb') as e:
    process=subprocess.Popen(cmd,stdout=o,stderr=e,cwd=exe.parent)
    write(OUT/'launch.json',{'pid':process.pid,'command':cmd,'exe_sha256':build['sha256'],'observer_sha256':sha(script),'profile_off':True})
    print(process.pid,flush=True);code=process.wait(timeout=510)
write(OUT/'execution.json',{'actual_exit':code,'stderr_bytes':(OUT/'stderr.txt').stat().st_size})
if capture.exists():shutil.copytree(capture,OUT/'captures')
assert code==0 and (OUT/'stderr.txt').stat().st_size==0
logs=(OUT/'stdout.txt').read_text(encoding='utf-8')
rows=[json.loads(x.split('FULL_CHAPTER_RUNTIME_RESULT ',1)[1]) for x in logs.splitlines() if 'FULL_CHAPTER_RUNTIME_RESULT ' in x]
victory=next(x for x in rows if x['mode']=='victory')
assert (victory['tick'],victory['kills'],victory['growth']['level'])==(23862,3451,12)
observer=[json.loads(x.split('PACKAGED16_GPU_OBSERVER ',1)[1]) for x in logs.splitlines() if 'PACKAGED16_GPU_OBSERVER ' in x]
assert len(observer)==1 and observer[0]['counts']['epoch']==1 and observer[0]['counts']['shatters']==840
write(OUT/'RESULT.json',{'first_victory':victory,'observer':observer[0],'captures':len(list((OUT/'captures').glob('*.png'))),'scope':'Actual packaged GPU/normal QA policy, seed90131/defaultHP/earned growth. Not manual/heard audio/formal performance/visual approval.'})
assert sha(exe)==build['sha256']
print('PASS GPU16',flush=True)
