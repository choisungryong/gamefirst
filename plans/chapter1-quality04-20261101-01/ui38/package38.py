"""Explicit approved UI38 adoption/build. Unique outputs; never overwrite37."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, re, shutil, subprocess, sys
sys.dont_write_bytecode=True
ROOT=Path('C:/Project/d2r-combat-baseline')
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'full37'
ID='chapter1-full-candidate-20261107-38'
STAGE=Path('C:/Project/game-research/build-staging')/ID
OUT=ROOT/'builds/chapter1'/ID
PROOF=HERE/'package38'
BACKUP=Path('C:/Project/game-research/implementation-backups/chapter1-before38-20261107-01')
USER37=Path(os.environ['APPDATA'])/'AshenCloisterChapterOneQuality37'
USER38=Path(os.environ['APPDATA'])/'AshenCloisterChapterOneQuality38'
ENGINE=Path('C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe')
NEW=['chapter1/view/ui38/chapter_hud_quality38.gd','chapter1/view/ui38/life_seal.gd','chapter1/view/ui38/element_seal.gd']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def check(base,pins):
    bad=[p for p,h in pins.items() if not (base/p).is_file() or sha(base/p)!=h]
    assert not bad,{'base':str(base),'mismatches':bad}
def files():
    paths=read(OLD/'build/closure.json')['runtime_source_files']+NEW
    assert len(paths)==166 and len(set(paths))==166
    return sorted(paths)
def profiles(folder):
    paths=[folder/'chapter-one-profile-v1.json']+sorted(folder.glob('chapter-one-profile-v1.revision-*.json'))
    assert all(p.is_file() for p in paths)
    return {str(p):sha(p) for p in paths}
def no_games():
    result=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object {$_.Name -like 'Godot*' -or $_.Name -like 'AshenCloister*'} | Select-Object -ExpandProperty ProcessId"],capture_output=True,text=True,check=True)
    assert not result.stdout.strip(),{'active_game_or_engine':result.stdout}
def preserve(pins):
    check(Path('.'),pins['absolute'])
    check(Path(pins['stage37']),pins['stage37_files'])
    assert profiles(USER37)==pins['user37'],'User37 changed; preserve and stop'
def execute(label,args,timeout=300):
    proc=subprocess.Popen([str(x) for x in args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',errors='replace')
    timed_out=False
    try:out,err=proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out=True;proc.terminate()
        try:out,err=proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:proc.kill();out,err=proc.communicate()
    result={'command':[str(x) for x in args],'owned_pid':proc.pid,'actual_exit':proc.returncode,'timed_out':timed_out,'stdout':out,'stderr':err}
    write(PROOF/(label+'-execution.json'),result)
    assert not timed_out and proc.returncode==0 and not re.search(r'SCRIPT ERROR|ERROR:|Parse Error',out+err),result
    return result
def adopt():
    no_games()
    assert not any(p.exists() for p in [BACKUP,USER38,PROOF,STAGE,OUT]),'All38 destinations must initially be absent'
    freeze=read(OLD/'FINAL-SOURCE-FREEZE.json');check(ROOT,freeze)
    closure=read(OLD/'build/closure.json');oldstage=Path(closure['stage'])
    stagepins=read(OLD/'build/staging-manifest.json');check(oldstage,stagepins)
    oldbuild=read(OLD/'build/build.json');assert sha(oldbuild['exe'])==oldbuild['sha256']
    pins={'absolute':{str(OLD/'FINAL-SOURCE-FREEZE.json'):sha(OLD/'FINAL-SOURCE-FREEZE.json'),str(OLD/'build/closure.json'):sha(OLD/'build/closure.json'),str(OLD/'build/staging-manifest.json'):sha(OLD/'build/staging-manifest.json'),oldbuild['exe']:oldbuild['sha256']},'stage37':str(oldstage),'stage37_files':stagepins,'user37':profiles(USER37)}
    current=read(USER37/'chapter-one-profile-v1.json')
    assert current['schema_version']==1 and len(current['items'])<=325
    BACKUP.mkdir();PROOF.mkdir()
    before={p:sha(ROOT/p) for p in files()+['project.godot','export_presets.cfg']}
    write(BACKUP/'FULL-ROOT-CLOSURE-BEFORE.json',before)
    for p in ['chapter1/chapter_one_view.gd','project.godot','export_presets.cfg']+NEW:
        target=BACKUP/'source'/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/p,target)
    shutil.copy2(OLD/'FINAL-SOURCE-FREEZE.json',BACKUP/'ORIGINAL37-FREEZE.json')
    USER38.mkdir();copies=[]
    for source,h in pins['user37'].items():
        source=Path(source);body=source.read_bytes();assert hashlib.sha256(body).hexdigest()==h
        target=USER38/source.name
        with target.open('xb') as f:f.write(body)
        target_backup=BACKUP/'user37-readonly-snapshot'/source.name;target_backup.parent.mkdir(exist_ok=True)
        with target_backup.open('xb') as f:f.write(body)
        assert sha(target)==sha(target_backup)==h
        copies.append({'source':str(source),'target':str(target),'snapshot':str(target_backup),'sha256':h})
    preserve(pins)
    write(PROOF/'PRESERVED37.json',pins)
    write(PROOF/'USER-FORK.json',{'mode':'One-time byte-identical latest37 fork into initially absent38; no schema rewrite or persistence call','copies':copies,'source_summary':{'revision':current['revision'],'items':len(current['items']),'equipped':current['equipped'],'completed_runs':current['completed_runs']}})
    assembly=ROOT/'chapter1/chapter_one_view.gd';body=assembly.read_bytes()
    old=b'res://chapter1/view/chapter_hud_quality36.gd';new=b'res://chapter1/view/ui38/chapter_hud_quality38.gd'
    assert body.count(old)==1;assembly.write_bytes(body.replace(old,new))
    after={p:sha(ROOT/p) for p in before}
    assert [p for p in before if before[p]!=after[p]]==['chapter1/chapter_one_view.gd']
    write(PROOF/'SOURCE-BEFORE.json',before);write(PROOF/'FINAL-SOURCE-FREEZE.json',after)
    write(PROOF/'ADOPTION.json',{'root_approved':True,'backup':str(BACKUP),'runtime_count':166,'tracked_new_files':{p:after[p] for p in NEW},'changed_existing_files':['chapter1/chapter_one_view.gd'],'core_data_unchanged':True,'source37_freeze':str(OLD/'FINAL-SOURCE-FREEZE.json')})
    preserve(pins)
    print(json.dumps({'adopted':True,'profile38_forked':len(copies),'runtime':166}))
def build():
    no_games();pins=read(PROOF/'PRESERVED37.json');preserve(pins)
    frozen=read(PROOF/'FINAL-SOURCE-FREEZE.json');check(ROOT,frozen)
    assert not STAGE.exists() and not OUT.exists()
    STAGE.mkdir();OUT.mkdir(parents=True)
    for p in files():
        target=STAGE/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/p,target)
    project=(ROOT/'project.godot').read_text(encoding='utf-8')
    assert project.count('run/main_scene="res://Baseline.tscn"')==1
    project=project.replace('run/main_scene="res://Baseline.tscn"','run/main_scene="res://chapter1/ChapterOne.tscn"')
    project=project.replace('config/name="D2R Combat Baseline"','config/name="Ashen Cloister ChapterOne Quality38"\nconfig/use_custom_user_dir=true\nconfig/custom_user_dir_name="AshenCloisterChapterOneQuality38"')
    project=project.replace('[rendering]','[rendering]\nanti_aliasing/quality/msaa_3d=2')
    (STAGE/'project.godot').write_text(project,encoding='utf-8')
    # Preserve37's audited explicit export filters, adding only the three own UI scripts.
    preset=(Path(pins['stage37'])/'export_presets.cfg').read_text(encoding='utf-8')
    preset=preset.replace('ChapterOne Quality37 Windows','ChapterOne Quality38 Windows')
    assert preset.count('export_files=PackedStringArray(')==1
    marker='export_files=PackedStringArray('
    preset=preset.replace(marker,marker+', '.join(json.dumps('res://'+p) for p in NEW)+', ')
    (STAGE/'export_presets.cfg').write_text(preset,encoding='utf-8')
    stagepins={p:sha(STAGE/p) for p in files()+['project.godot','export_presets.cfg']}
    write(PROOF/'staging-manifest.json',stagepins)
    write(PROOF/'closure.json',{'build_id':ID,'runtime_source_files':files(),'source_count':166,'stage_count':168,'stage':str(STAGE),'output':str(OUT),'scope':'HUD38 only; Core37/World37c/Actor36/FX36/Input21 unchanged'})
    execute('import',[ENGINE,'--headless','--path',STAGE,'--editor','--import','--quit'])
    exe=OUT/'AshenCloister-Chapter1.exe'
    execute('export',[ENGINE,'--headless','--path',STAGE,'--export-release','ChapterOne Quality38 Windows',exe])
    check(ROOT,frozen);check(STAGE,stagepins);preserve(pins)
    spec=importlib.util.spec_from_file_location('pck_parser',ROOT/'tools/build_phase7.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
    pck=parser.pck_entries(exe);packed={r['path'].removeprefix('res://'):r for r in pck['entries']}
    for p in files():
        ext=Path(p).suffix;expected=p+'.import' if ext in ['.png','.wav','.glb','.svg'] else p+'.remap' if ext in ['.gd','.tscn'] else p
        assert expected in packed or ext=='.gdshader' and p+'.remap' in packed,('Missing dependency',p)
        if ext in ['.json','.txt','.md']:assert packed[p]['sha256']==frozen[p]
    bad=[p for p in packed if any(term in p.lower() for term in ['plans/','research/','tests/','tools/','evidence/','baseline.tscn','ui38_probe','world_preview'])]
    assert not bad,bad
    write(PROOF/'pck-audit.json',{'entries':pck['entries'],'forbidden_matches':bad,'success':True})
    # Existing audited credits already correspond exactly to unchanged166 dependency set.
    shutil.copytree(Path(read(OLD/'build/build.json')['exe']).parent/'credits',OUT/'credits')
    (OUT/'RUN.ko.md').write_text('# 잿빛 회랑 · 후보38\n\nAshenCloister-Chapter1.exe를 실행하세요. UI38 개선본입니다. WASD/좌클릭 이동, Space 회피, Q 회복약, I 장비, Esc 정지. 기존37 진행을 별도38 저장 공간에 한 번 복사했습니다. 이후37/38 진행은 별개입니다. 기존37 실행본과 저장은 보존했습니다. 최종 성능/전체 수동 완주/청취 승인은 별도입니다.\n',encoding='utf-8')
    write(PROOF/'build.json',{'exe':str(exe),'sha256':sha(exe),'bytes':exe.stat().st_size,'runtime_count':166,'stage_count':168,'pck_count':len(packed),'scope':'UI38 executable package; no full performance/manual completion claim'})
    print(json.dumps(read(PROOF/'build.json')))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['adopt','build']);args=ap.parse_args()
    adopt() if args.action=='adopt' else build()
