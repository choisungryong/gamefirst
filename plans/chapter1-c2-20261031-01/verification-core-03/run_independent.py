from pathlib import Path
import hashlib, json, subprocess, sys

ROOT = Path('C:/Project/d2r-combat-baseline')
HERE = Path(__file__).resolve().parent
ENGINE = Path('C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe')
FROZEN = ROOT/'chapter1/evidence/core-pilot-20261031-03'

def write(name, value):
    p = HERE/name
    assert not p.exists(), 'Refusing to overwrite evidence: '+str(p)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def pins():
    out=[]
    for entry in json.loads((FROZEN/'source-manifest.json').read_text(encoding='utf-8')):
        p=entry['path']; expected=entry['sha256']
        current=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
        saved=hashlib.sha256((FROZEN/'source'/p).read_bytes()).hexdigest()
        out.append({'path':p,'expected':expected,'current':current,'saved':saved,'match':expected==current==saved})
    return out

def run(label, script, args=()):
    command=[str(ENGINE),'--headless','--path',str(ROOT),'--script',script,'--',*args]
    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    write(label+'-execution.json',{'command':command,'cwd':str(ROOT),'actual_exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    print(label,result.returncode,result.stdout[-1200:])
    return result.returncode

if __name__=='__main__':
    before=pins();write('pins-before.json',before)
    assert all(e['match'] for e in before)
    codes={}
    codes['functional']=run('functional','res://chapter1/tests/test_combat_run.gd')
    codes['negative']=run('negative','res://chapter1/tests/test_combat_run.gd',['--prove-failure'])
    codes['independent']=run('independent','res://plans/chapter1-c2-20261031-01/verification-core-03/independent.gd')
    codes['normal']=run('normal','res://chapter1/tests/pilot_combat_run.gd',['--output='+str(HERE/'normal-results.json')])
    after=pins();write('pins-after.json',after)
    write('execution-summary.json',{'codes':codes,'pins_unchanged':before==after,'pin_matches':all(e['match'] for e in after),'expected_normal_success':False,'scope':'Independent headless functional/boundary verification; no visual/audio/GPU/OS quality approval'})
    sys.exit(0 if codes=={'functional':0,'negative':1,'independent':0,'normal':1} and before==after and all(e['match'] for e in after) else 1)
