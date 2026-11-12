"""Resume isolated refactor verification; never edits a released payload/save."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys

ROOT=Path('C:/Project/d2r-combat-baseline')
BASE=ROOT/'plans/chapter1-quality04-20261101-01'
HERE=Path(__file__).resolve().parent/'resume02'
STAGE=Path('C:/Project/game-research/build-staging/actor42-refactor-exact02')
ENGINE=Path('C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe')
PARENTS=['chapter_actors_demon19.gd','chapter_actors_quality21.gd']
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
    with Path(p).open('x',encoding='utf-8') as f: json.dump(v,f,ensure_ascii=False,indent=2)
def pins():
    freeze=read(BASE/'full41/FINAL-SOURCE-FREEZE.json')
    for p,h in freeze.items(): assert sha(ROOT/p)==h,('released root changed',p)
    users={str(p):sha(p) for d in (Path.home()/'AppData/Roaming').glob('AshenCloisterChapterOneQuality*') for p in d.glob('chapter-one-profile-v1*.json')}
    return {'root41':freeze,'users':users,'exe41':sha(read(BASE/'full41/build.json')['exe'])}
def prepare():
    assert not HERE.exists() and not STAGE.exists(), 'Preserve existing attempt'
    before=pins(); HERE.mkdir(); STAGE.mkdir()
    closure=read(BASE/'full41/closure.json')
    for name in closure['runtime_source_files']:
        dst=STAGE/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dst)
    oldstage=Path(closure['stage'])
    for name in ['project.godot','export_presets.cfg']:shutil.copy2(oldstage/name,STAGE/name)
    p=STAGE/'project.godot'
    t=p.read_text(encoding='utf-8').replace('AshenCloisterChapterOneQuality41','AshenCloisterDiagnostic42Refactor02')
    p.write_text(t,encoding='utf-8')
    for name in PARENTS:
        shutil.copy2(BASE/'performance42-actors/refactor-candidate'/name,STAGE/'chapter1/view'/name)
    for name in ['chapter_actors_quality42.gd','chapter_actors_quality42_verify.gd']:
        shutil.copy2(ROOT/'chapter1/view'/name,STAGE/'chapter1/view'/name)
    artifacts=ROOT/'artifacts/performance42-actors'
    for src,dst in [('full42b.gd','full.gd'),('extended42b.gd','extended.gd'),('exact42b.gd','exact.gd'),('view42b.gd','view42b.gd')]:
        t=(artifacts/src).read_text(encoding='utf-8').replace('chapter_actors_quality42b.gd','chapter_actors_quality42.gd')
        (STAGE/dst).write_text(t,encoding='utf-8')
    write(HERE/'PRESERVATION-BEFORE.json',before)
    write(HERE/'STAGE.json',{'stage':str(STAGE),'payload':{str(p.relative_to(STAGE)):sha(p) for p in STAGE.rglob('*') if p.is_file()}})
    assert pins()==before
    print('PREPARED',STAGE,flush=True)
def execute(label,args):
    assert HERE.exists()
    output=HERE/(label+'.json');assert not output.exists(),'Never overwrite evidence'
    before=pins()
    r=subprocess.run([str(ENGINE),*args],capture_output=True,timeout=240)
    for stream in ['stdout','stderr']:
        raw=getattr(r,stream);(HERE/(label+'.'+stream+'.bin')).write_bytes(raw)
        try: decoded=raw.decode('utf-8')
        except UnicodeDecodeError: decoded=raw.decode('cp949',errors='replace')
        setattr(r,stream,decoded)
        (HERE/(label+'.'+stream+'.txt')).write_text(decoded,encoding='utf-8')
    after=pins()
    bad=any(s in r.stdout+r.stderr for s in ['SCRIPT ERROR','Parse Error','ERROR:'])
    result={'command':[str(ENGINE),*args],'exit':r.returncode,'errors':bad,'preserved':before==after,'stdout':r.stdout[-1800:],'stderr':r.stderr}
    write(output,result)
    print(json.dumps(result,ensure_ascii=False),flush=True)
    assert r.returncode==0 and not bad and before==after
if __name__=='__main__':
    action=sys.argv[1]
    if action=='prepare':prepare()
    elif action=='import':execute('import',['--headless','--path',str(STAGE),'--editor','--import','--quit'])
    else:execute(action,['--headless','--path',str(STAGE),'--script','res://'+action+'.gd','--','--chapter1-profile-off'])
