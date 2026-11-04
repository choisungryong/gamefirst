from pathlib import Path
import hashlib,json,shutil,subprocess,sys
ROOT=Path('C:/Project/d2r-combat-baseline')
OUT=Path(__file__).resolve().parent
ENGINE=Path('C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,data):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
def backup():
    dest=Path('C:/Project/game-research/implementation-backups/chapter1-quality04-root-resume-before-20261101-01')
    assert not dest.exists(),'Preserve earlier backup'
    old=json.loads((ROOT/'plans/chapter1-quality-20261031-01/package03/build/source-manifest.json').read_text(encoding='utf-8'))
    names=sorted(set(old)|{'chapter1/presentation/frame_probe.gd','chapter1/view/hero_occlusion_rim.gdshader','HANDOFF.md'})
    pins={}
    for name in names:
        target=dest/'source'/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,target)
        pins[name]=sha(ROOT/name)
        assert sha(target)==pins[name]
    write(dest/'manifest.json',{'source_count':len(pins),'files':pins,'scope':'Current interrupted quality04 before root repairs; prior03/04 evidence kept'})
    write(OUT/'BACKUP.json',{'path':str(dest),'manifest_sha256':sha(dest/'manifest.json'),'count':len(pins)})
    print(json.dumps({'backup':str(dest),'count':len(pins)}))
def run(label,script,args):
    target=OUT/(label+'-execution.json');assert not target.exists()
    command=[str(ENGINE),'--headless','--path',str(ROOT),'--script',script]
    if args:command+=['--']+args
    try:
        r=subprocess.run(command,capture_output=True,timeout=180)
        data={'command':command,'actual_exit':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace')}
    except subprocess.TimeoutExpired as e:
        data={'command':command,'actual_exit':None,'timed_out':True,'stdout':(e.stdout or b'').decode('utf-8','replace'),'stderr':(e.stderr or b'').decode('utf-8','replace')}
    write(target,data)
    print(json.dumps(data,ensure_ascii=False))
if __name__=='__main__':
    if sys.argv[1]=='backup':backup()
    else:run(sys.argv[1],sys.argv[2],sys.argv[3:])
