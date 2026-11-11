"""Candidate40 explicit closure package. Adoption/build require root's later GO.

prepare only reads source facts; it never imports, exports, forks saves or adopts.
All generated evidence uses exclusive writes and unique40 destinations.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, re, shutil, subprocess, sys
sys.dont_write_bytecode=True
ROOT=Path('C:/Project/d2r-combat-baseline')
HERE=Path(__file__).resolve().parent
OLD38=HERE.parent/'ui38/package38'
OLD37=HERE.parent/'full37'
ID='chapter1-full-candidate-20261111-40'
STAGE=Path('C:/Project/game-research/build-staging')/ID
OUT=ROOT/'builds/chapter1'/ID
BACKUP=Path('C:/Project/game-research/implementation-backups/chapter1-before40-20261111-01')
USER37=Path(os.environ['APPDATA'])/'AshenCloisterChapterOneQuality37'
USER38=Path(os.environ['APPDATA'])/'AshenCloisterChapterOneQuality38'
USER40=Path(os.environ['APPDATA'])/'AshenCloisterChapterOneQuality40'
ENGINE=Path('C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe')
NEW=['chapter1/view/chapter_elements_quality39.gd',
     'chapter1/view/frost_core_quality39.gdshader',
     'chapter1/view/frost_contact_quality39.gdshader',
     'chapter1/view/frost_fracture_quality39.gdshader',
     'chapter1/view/frost_release_quality39.gdshader',
     'chapter1/view/ui40/chapter_hud_quality40.gd']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,value):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def check(base,pins):
    bad=[p for p,h in pins.items() if not (base/p).is_file() or sha(base/p)!=h]
    assert not bad,{'base':str(base),'mismatches':bad}
def files():
    paths=read(OLD38/'closure.json')['runtime_source_files']+NEW
    assert len(paths)==172 and len(set(paths))==172
    assert all((ROOT/p).is_file() for p in paths)
    return sorted(paths)
def profiles(folder):
    paths=[folder/'chapter-one-profile-v1.json']+sorted(folder.glob('chapter-one-profile-v1.revision-*.json'))
    assert all(p.is_file() for p in paths),str(folder)
    return {str(p):sha(p) for p in paths}
def no_games():
    result=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object {$_.Name -like 'Godot*' -or $_.Name -like 'AshenCloister*'} | Select-Object -ExpandProperty ProcessId"],capture_output=True,text=True,check=True)
    assert not result.stdout.strip(),{'active_game_or_engine':result.stdout}
def preserve(pins,include40=True):
    check(Path('.'),pins['absolute'])
    for stage in pins['stages']:check(Path(stage['path']),stage['files'])
    check(ROOT,pins['unchanged_root38'])
    assert profiles(USER37)==pins['user37'],'Current37 progress changed; preserve and stop'
    assert profiles(USER38)==pins['user38'],'Current38 progress changed; preserve and stop'
    if include40:assert profiles(USER40)==pins['user40'],'Fork40 progress changed; preserve and stop'
def execute(label,args,timeout=300):
    proc=None;out='';err='';timed_out=False;launch_error=None
    try:
        proc=subprocess.Popen([str(x) for x in args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',errors='replace')
        try:out,err=proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out=True;proc.terminate()
            try:out,err=proc.communicate(timeout=10)
            except subprocess.TimeoutExpired:proc.kill();out,err=proc.communicate()
    except OSError as error:launch_error=repr(error)
    result={'command':[str(x) for x in args],'owned_pid':None if proc is None else proc.pid,'actual_exit':None if proc is None else proc.returncode,'timed_out':timed_out,'launch_error':launch_error,'stdout':out,'stderr':err}
    write(HERE/(label+'-execution.json'),result)
    assert not timed_out and launch_error is None and proc.returncode==0 and not re.search(r'SCRIPT ERROR|ERROR:|Parse Error',out+err),result
    return result
def prepare():
    print(json.dumps({'build_id':ID,'runtime_count':len(files()),'stage_count':len(files())+2,'new_files':NEW,'stage':str(STAGE),'output':str(OUT),'proof':str(HERE),'backup':str(BACKUP),'user40':str(USER40),'adoption_or_fork_or_engine_started':False},ensure_ascii=False))
def adopt():
    no_games()
    assert not any(p.exists() for p in [BACKUP,USER40,STAGE,OUT]),'All40 destination directories must initially be absent'
    assert not any((HERE/p).exists() for p in ['ADOPTION.json','PRESERVED.json','SOURCE-BEFORE.json','FINAL-SOURCE-FREEZE.json','USER-FORK.json']),'40 adoption evidence already exists; never overwrite'
    freeze38=read(OLD38/'FINAL-SOURCE-FREEZE.json');check(ROOT,freeze38)
    absolute={str(p):sha(p) for p in [OLD38/'FINAL-SOURCE-FREEZE.json',OLD38/'closure.json',OLD38/'staging-manifest.json',OLD38/'build.json',OLD37/'FINAL-SOURCE-FREEZE.json',OLD37/'build/closure.json',OLD37/'build/staging-manifest.json',OLD37/'build/build.json']}
    stages=[]
    for folder in [OLD38,OLD37/'build']:
        closure=read(folder/'closure.json');stagepins=read(folder/'staging-manifest.json');stage=Path(closure['stage']);check(stage,stagepins)
        build=read(folder/'build.json');assert sha(build['exe'])==build['sha256']
        absolute[build['exe']]=build['sha256'];stages.append({'path':str(stage),'files':stagepins})
    user37=profiles(USER37);user38=profiles(USER38)
    current=read(USER38/'chapter-one-profile-v1.json')
    assert current['schema_version']==1 and len(current['items'])<=325
    before={p:sha(ROOT/p) for p in files()+['project.godot','export_presets.cfg']}
    BACKUP.mkdir()
    write(BACKUP/'FULL-ROOT-CLOSURE-BEFORE.json',before)
    for p in ['chapter1/chapter_one_view.gd','project.godot','export_presets.cfg']+NEW:
        target=BACKUP/'source'/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/p,target)
    shutil.copy2(OLD38/'FINAL-SOURCE-FREEZE.json',BACKUP/'ORIGINAL38-FREEZE.json')
    for label,pins in [('user37',user37),('user38',user38)]:
        snapshot=BACKUP/(label+'-readonly-snapshot');snapshot.mkdir()
        for source,h in pins.items():
            body=Path(source).read_bytes();assert hashlib.sha256(body).hexdigest()==h
            target=snapshot/Path(source).name
            with target.open('xb') as f:f.write(body)
            assert sha(target)==h
    USER40.mkdir();copies=[]
    for source,h in user38.items():
        body=Path(source).read_bytes();assert hashlib.sha256(body).hexdigest()==h
        target=USER40/Path(source).name
        with target.open('xb') as f:f.write(body)
        assert sha(target)==h
        copies.append({'source':source,'target':str(target),'sha256':h})
    pins={'absolute':absolute,'stages':stages,'unchanged_root38':{p:h for p,h in freeze38.items() if p!='chapter1/chapter_one_view.gd'},'user37':user37,'user38':user38,'user40':profiles(USER40)}
    preserve(pins)
    write(HERE/'PRESERVED.json',pins)
    write(HERE/'USER-FORK.json',{'mode':'One-time byte-identical CURRENT38 main and all revision journals into initially absent40; no rewrite/reset/award/persist','copies':copies,'source_summary':{'revision':current['revision'],'items':len(current['items']),'equipped':current['equipped'],'completed_runs':current['completed_runs']}})
    assembly=ROOT/'chapter1/chapter_one_view.gd';body=assembly.read_bytes()
    for old,new in [(b'res://chapter1/view/ui38/chapter_hud_quality38.gd',b'res://chapter1/view/ui40/chapter_hud_quality40.gd'),(b'res://chapter1/view/chapter_elements_quality36.gd',b'res://chapter1/view/chapter_elements_quality39.gd')]:
        assert body.count(old)==1;body=body.replace(old,new)
    assembly.write_bytes(body)
    after={p:sha(ROOT/p) for p in before}
    assert [p for p in before if before[p]!=after[p]]==['chapter1/chapter_one_view.gd']
    write(HERE/'SOURCE-BEFORE.json',before);write(HERE/'FINAL-SOURCE-FREEZE.json',after)
    write(HERE/'ADOPTION.json',{'root_approved':True,'backup':str(BACKUP),'runtime_count':172,'new_files':{p:after[p] for p in NEW},'changed_existing_files':['chapter1/chapter_one_view.gd'],'core_data_audio_models_unchanged':True,'preserved38_freeze':str(OLD38/'FINAL-SOURCE-FREEZE.json')})
    preserve(pins)
    print(json.dumps({'adopted':True,'profile40_forked':len(copies),'runtime':172}))
def build():
    no_games();pins=read(HERE/'PRESERVED.json');preserve(pins)
    frozen=read(HERE/'FINAL-SOURCE-FREEZE.json');check(ROOT,frozen)
    assert not STAGE.exists() and not OUT.exists()
    STAGE.mkdir();OUT.mkdir(parents=True)
    for p in files():
        target=STAGE/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/p,target)
    project=(ROOT/'project.godot').read_text(encoding='utf-8')
    assert project.count('run/main_scene="res://Baseline.tscn"')==1
    project=project.replace('run/main_scene="res://Baseline.tscn"','run/main_scene="res://chapter1/ChapterOne.tscn"')
    project=project.replace('config/name="D2R Combat Baseline"','config/name="Ashen Cloister ChapterOne Quality40"\nconfig/use_custom_user_dir=true\nconfig/custom_user_dir_name="AshenCloisterChapterOneQuality40"')
    project=project.replace('[rendering]','[rendering]\nanti_aliasing/quality/msaa_3d=2')
    (STAGE/'project.godot').write_text(project,encoding='utf-8')
    oldstage=Path(read(OLD38/'closure.json')['stage'])
    preset=(oldstage/'export_presets.cfg').read_text(encoding='utf-8').replace('ChapterOne Quality38 Windows','ChapterOne Quality40 Windows')
    marker='export_files=PackedStringArray(';assert preset.count(marker)==1
    preset=preset.replace(marker,marker+', '.join(json.dumps('res://'+p) for p in NEW)+', ')
    (STAGE/'export_presets.cfg').write_text(preset,encoding='utf-8')
    stagepins={p:sha(STAGE/p) for p in files()+['project.godot','export_presets.cfg']}
    write(HERE/'staging-manifest.json',stagepins)
    write(HERE/'closure.json',{'build_id':ID,'runtime_source_files':files(),'source_count':172,'stage_count':174,'stage':str(STAGE),'output':str(OUT),'scope':'HUD40+FX39; Core37/World37c/Actor36/Input21/audio/models unchanged'})
    execute('import',[ENGINE,'--headless','--path',STAGE,'--editor','--import','--quit'])
    exe=OUT/'AshenCloister-Chapter1.exe'
    execute('export',[ENGINE,'--headless','--path',STAGE,'--export-release','ChapterOne Quality40 Windows',exe])
    check(ROOT,frozen);check(STAGE,stagepins);preserve(pins)
    audit()
def audit():
    # Resumable read-only audit of the same successful export, never a re-export.
    no_games();pins=read(HERE/'PRESERVED.json');preserve(pins)
    frozen=read(HERE/'FINAL-SOURCE-FREEZE.json');check(ROOT,frozen)
    stagepins=read(HERE/'staging-manifest.json');check(STAGE,stagepins)
    exported=read(HERE/'export-execution.json')
    exe=OUT/'AshenCloister-Chapter1.exe'
    assert exported['actual_exit']==0 and not exported['timed_out'] and exported['launch_error'] is None and exported['command'][-1]==str(exe)
    assert exe.is_file() and not (HERE/'pck-audit.json').exists() and not (HERE/'build.json').exists()
    spec=importlib.util.spec_from_file_location('pck_parser',ROOT/'tools/build_phase7.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
    pck=parser.pck_entries(exe);packed={row['path'].removeprefix('res://'):row for row in pck['entries']}
    for p in files():
        ext=Path(p).suffix;expected=p+'.import' if ext in ['.png','.wav','.glb','.svg'] else p+'.remap' if ext in ['.gd','.tscn'] else p
        assert expected in packed or ext=='.gdshader' and p+'.remap' in packed,('Missing dependency',p)
        if ext in ['.json','.txt','.md']:assert packed[p]['sha256']==frozen[p]
    bad=[p for p in packed if any(term in p.lower() for term in ['plans/','research/','tests/','tools/','evidence/','baseline.tscn','ui38_probe','ui40_probe','packaged40_integration','frost39_compare','world_preview','portrait41'])]
    assert not bad,bad
    write(HERE/'pck-audit.json',{'entries':pck['entries'],'forbidden_matches':bad,'success':True})
    shutil.copytree(Path(read(OLD38/'build.json')['exe']).parent/'credits',OUT/'credits')
    (OUT/'RUN.ko.md').write_text('# 잿빛 회랑 · 후보40\n\nAshenCloister-Chapter1.exe를 실행하세요. 보관함·진행 안내·결과 UI와 냉기 표현 개선본입니다. WASD/좌클릭 이동, Space 회피, Q 회복약, I 장비, Esc 정지. 현재38 진행을 별도40 저장 공간에 한 번 복사했고 이후 진행은 독립입니다. 기존37/38 실행본과 저장은 보존했습니다. 최종 성능·전체 수동 완주·음향 승인은 별도입니다.\n',encoding='utf-8')
    write(HERE/'build.json',{'exe':str(exe),'sha256':sha(exe),'bytes':exe.stat().st_size,'runtime_count':172,'stage_count':174,'pck_count':len(packed),'scope':'HUD40+FX39 package; no full performance/manual completion claim'})
    print(json.dumps(read(HERE/'build.json')))
def verify():
    no_games();pins=read(HERE/'PRESERVED.json');preserve(pins)
    frozen=read(HERE/'FINAL-SOURCE-FREEZE.json');check(ROOT,frozen)
    stagepins=read(HERE/'staging-manifest.json');check(STAGE,stagepins)
    exe=Path(read(HERE/'build.json')['exe'])
    assert sha(exe)==read(HERE/'build.json')['sha256']
    native=HERE/'native01';assert not native.exists();native.mkdir()
    execute('packaged-integration',[exe,'--position','20,20','--script',HERE/'packaged40_integration.gd','--','--ui40-output='+str(native)],timeout=120)
    result=read(native/'PACKAGED-INTEGRATION.json');assert result['success'] is True
    write(HERE/'PACKAGED-INTEGRATION.json',result)
    preserve(pins);check(ROOT,frozen);check(STAGE,stagepins)
    write(HERE/'FINAL-PRESERVATION.json',{'success':True,'preserved_previous_builds':True,'source40_and_stage40_unchanged':True,'user37_count':len(pins['user37']),'user38_count':len(pins['user38']),'user40_count':len(pins['user40']),'profiles_byte_identical':True})
    print(json.dumps({'integration':result['success'],'checks':len(result['checks']),'previous_and_fork_profiles_unchanged':True}))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','adopt','build','audit','verify']);action=parser.parse_args().action
    {'prepare':prepare,'adopt':adopt,'build':build,'audit':audit,'verify':verify}[action]()
