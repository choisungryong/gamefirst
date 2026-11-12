"""Candidate42 explicit closure package. Adoption/build require root's later GO.

prepare only reads source facts; it never imports, exports, forks saves or adopts.
All generated evidence uses exclusive writes and unique42 destinations.
Prepared only: no source42 freeze, adoption, save fork or engine launch authorized yet.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, re, shutil, subprocess, sys
sys.dont_write_bytecode=True
ROOT=Path('C:/Project/d2r-combat-baseline')
HERE=Path(__file__).resolve().parent
OLD41=HERE.parent/'full41'
OLD38=HERE.parent/'ui38/package38'
OLD37=HERE.parent/'full37'
ID='chapter1-full-candidate-20261113-42'
STAGE=Path('C:/Project/game-research/build-staging')/ID
OUT=ROOT/'builds/chapter1'/ID
BACKUP=Path('C:/Project/game-research/implementation-backups/chapter1-before42-20261113-01')
USER37=Path(os.environ['APPDATA'])/'AshenCloisterChapterOneQuality37'
USER38=Path(os.environ['APPDATA'])/'AshenCloisterChapterOneQuality38'
USER40=Path(os.environ['APPDATA'])/'AshenCloisterChapterOneQuality40'
USER41=Path(os.environ['APPDATA'])/'AshenCloisterChapterOneQuality41'
USER42=Path(os.environ['APPDATA'])/'AshenCloisterChapterOneQuality42'
ENGINE=Path('C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe')
NEW=['chapter1/view/chapter_actors_quality42.gd']
PARENTS=['chapter1/view/chapter_actors_demon19.gd','chapter1/view/chapter_actors_quality21.gd']
CHANGED=['chapter1/chapter_one_view.gd']+PARENTS
CANDIDATE=HERE.parent/'performance42-actors/refactor-candidate'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,value):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def check(base,pins):
    bad=[p for p,h in pins.items() if not (base/p).is_file() or sha(base/p)!=h]
    assert not bad,{'base':str(base),'mismatches':bad}
def files():
    paths=read(OLD41/'closure.json')['runtime_source_files']+NEW
    assert len(paths)==176 and len(set(paths))==176
    assert all((ROOT/p).is_file() for p in paths)
    return sorted(paths)
def profiles(folder):
    paths=[folder/'chapter-one-profile-v1.json']+sorted(folder.glob('chapter-one-profile-v1.revision-*.json'))
    assert all(p.is_file() for p in paths),str(folder)
    return {str(p):sha(p) for p in paths}
def no_games():
    result=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object {$_.Name -like 'Godot*' -or $_.Name -like 'AshenCloister*'} | Select-Object -ExpandProperty ProcessId"],capture_output=True,text=True,check=True)
    assert not result.stdout.strip(),{'active_game_or_engine':result.stdout}
def preserve(pins,include42=True):
    check(Path('.'),pins['absolute'])
    for stage in pins['stages']:check(Path(stage['path']),stage['files'])
    check(ROOT,pins['unchanged_root41'])
    for number,folder in [(37,USER37),(38,USER38),(40,USER40),(41,USER41)]:
        assert profiles(folder)==pins['user'+str(number)],'Current progress changed; preserve and stop: '+str(number)
    if include42:assert profiles(USER42)==pins['user42'],'Fork42 progress changed; preserve and stop'
    first_path=OLD41/'ATTEMPT01-PRESERVED.json'
    if first_path.exists():
        first=read(first_path);check(Path(first['stage']),first['stage_files'])
        assert sha(first['exe'])==first['exe_sha256'],'Original attempt01 EXE changed'
        check(Path('.'),first['relocated_proof_hashes'])
def execute(label,args,timeout=300):
    assert not (HERE/(label+'-execution.json')).exists(),'Execution raw already exists; choose new unique attempt before launching'
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
    print(json.dumps({'build_id':ID,'runtime_count':len(files()),'stage_count':len(files())+2,'new_files':NEW,'stage':str(STAGE),'output':str(OUT),'proof':str(HERE),'backup':str(BACKUP),'user42':str(USER42),'adoption_or_fork_or_engine_started':False},ensure_ascii=False))
def adopt():
    no_games()
    selection=read(HERE/'SELECTION.json')
    assert selection['parity_passed'] is True and selection['native_improvement_confirmed'] is True
    check(ROOT,selection['root_files'])
    check(CANDIDATE,selection['candidate_parents'])
    assert read(OLD41/'build.json')['sha256']=='5da243815d2be1ce4a1e3e2265fac7fd4ef995275457d6da2a81d74188a545b2'
    assert not any(p.exists() for p in [BACKUP,USER42,STAGE,OUT]),'All42 destination directories must initially be absent'
    assert not any((HERE/p).exists() for p in ['ADOPTION.json','PRESERVED.json','SOURCE-BEFORE.json','FINAL-SOURCE-FREEZE.json','USER-FORK.json']),'42 adoption evidence already exists; never overwrite'
    freeze41=read(OLD41/'FINAL-SOURCE-FREEZE.json');check(ROOT,freeze41)
    absolute={};stages=[]
    for folder in [OLD41,HERE.parent/'full40',OLD38,OLD37/'build']:
        freeze_path=OLD37/'FINAL-SOURCE-FREEZE.json' if folder==OLD37/'build' else folder/'FINAL-SOURCE-FREEZE.json'
        for p in [freeze_path,folder/'closure.json',folder/'staging-manifest.json',folder/'build.json']:absolute[str(p)]=sha(p)
        closure=read(folder/'closure.json');stagepins=read(folder/'staging-manifest.json');stage=Path(closure['stage']);check(stage,stagepins)
        build=read(folder/'build.json');assert sha(build['exe'])==build['sha256']
        absolute[build['exe']]=build['sha256'];stages.append({'path':str(stage),'files':stagepins})
    userpins={str(number):profiles(folder) for number,folder in [(37,USER37),(38,USER38),(40,USER40),(41,USER41)]}
    current=read(USER41/'chapter-one-profile-v1.json')
    assert current['schema_version']==1 and len(current['items'])<=325
    before={p:sha(ROOT/p) for p in files()+['project.godot','export_presets.cfg']}
    BACKUP.mkdir()
    write(BACKUP/'FULL-ROOT-CLOSURE-BEFORE.json',before)
    for p in CHANGED+['project.godot','export_presets.cfg']+NEW:
        target=BACKUP/'source'/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/p,target)
    shutil.copy2(OLD41/'FINAL-SOURCE-FREEZE.json',BACKUP/'ORIGINAL41-FREEZE.json')
    for number,pins_ in userpins.items():
        snapshot=BACKUP/('user'+number+'-readonly-snapshot');snapshot.mkdir()
        for source,h in pins_.items():
            body=Path(source).read_bytes();assert hashlib.sha256(body).hexdigest()==h
            target=snapshot/Path(source).name
            with target.open('xb') as f:f.write(body)
            assert sha(target)==h
    USER42.mkdir();copies=[]
    for source,h in userpins['41'].items():
        body=Path(source).read_bytes();assert hashlib.sha256(body).hexdigest()==h
        target=USER42/Path(source).name
        with target.open('xb') as f:f.write(body)
        assert sha(target)==h
        copies.append({'source':source,'target':str(target),'sha256':h})
    pins={'absolute':absolute,'stages':stages,'unchanged_root41':{p:h for p,h in freeze41.items() if p not in CHANGED},'user42':profiles(USER42)}
    pins.update({'user'+number:pins_ for number,pins_ in userpins.items()})
    preserve(pins)
    write(HERE/'PRESERVED.json',pins)
    write(HERE/'USER-FORK.json',{'mode':'One-time byte-identical CURRENT41 main and all revision journals into initially absent42; no rewrite/reset/award/persist','copies':copies,'source_summary':{'revision':current['revision'],'items':len(current['items']),'equipped':current['equipped'],'completed_runs':current['completed_runs']}})
    assembly=ROOT/'chapter1/chapter_one_view.gd';body=assembly.read_bytes()
    old=b'res://chapter1/view/chapter_actors_quality36.gd';new=b'res://chapter1/view/chapter_actors_quality42.gd'
    assert body.count(old)==1;assembly.write_bytes(body.replace(old,new))
    for p in PARENTS:shutil.copy2(CANDIDATE/Path(p).name,ROOT/p)
    after={p:sha(ROOT/p) for p in before}
    assert sorted(p for p in before if before[p]!=after[p])==sorted(CHANGED)
    write(HERE/'SOURCE-BEFORE.json',before);write(HERE/'FINAL-SOURCE-FREEZE.json',after)
    write(HERE/'ADOPTION.json',{'root_approved':True,'backup':str(BACKUP),'runtime_count':176,'new_files':{p:after[p] for p in NEW},'changed_existing_files':CHANGED,'hud41_core_data_audio_models_fx39_unchanged':True,'preserved41_freeze':str(OLD41/'FINAL-SOURCE-FREEZE.json'),'selection':str(HERE/'SELECTION.json')})
    preserve(pins)
    print(json.dumps({'adopted':True,'profile42_forked':len(copies),'runtime':176}))
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
    project=project.replace('config/name="D2R Combat Baseline"','config/name="Ashen Cloister ChapterOne Quality42"\nconfig/use_custom_user_dir=true\nconfig/custom_user_dir_name="AshenCloisterChapterOneQuality42"')
    project=project.replace('[rendering]','[rendering]\nanti_aliasing/quality/msaa_3d=2')
    (STAGE/'project.godot').write_text(project,encoding='utf-8')
    oldstage=Path(read(OLD41/'closure.json')['stage'])
    preset=(oldstage/'export_presets.cfg').read_text(encoding='utf-8').replace('ChapterOne Quality41 Windows','ChapterOne Quality42 Windows')
    # Reuse successful41 preset byte-for-byte except title and actor42 export entry.
    assert 'chapter1/art/portrait41/ATTRIBUTION.ko.md' in preset.split('include_filter="',1)[1].split('"',1)[0].split(',')
    marker='export_files=PackedStringArray(';assert preset.count(marker)==1
    preset=preset.replace(marker,marker+', '.join(json.dumps('res://'+p) for p in NEW)+', ')
    (STAGE/'export_presets.cfg').write_text(preset,encoding='utf-8')
    stagepins={p:sha(STAGE/p) for p in files()+['project.godot','export_presets.cfg']}
    write(HERE/'staging-manifest.json',stagepins)
    write(HERE/'closure.json',{'build_id':ID,'runtime_source_files':files(),'source_count':176,'stage_count':178,'stage':str(STAGE),'output':str(OUT),'scope':'Actor42 inherits36 with redundant animation work elision; HUD41/FX39/Core37/data/audio/models unchanged'})
    execute('import',[ENGINE,'--headless','--path',STAGE,'--editor','--import','--quit'])
    exe=OUT/'AshenCloister-Chapter1.exe'
    execute('export',[ENGINE,'--headless','--path',STAGE,'--export-release','ChapterOne Quality42 Windows',exe])
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
    bad=[p for p in packed if any(term in p.lower() for term in ['plans/','research/','tests/','tools/','evidence/','baseline.tscn','ui38_probe','ui40_probe','ui41_probe','ui42_probe','packaged40_integration','packaged42_integration','frost39_compare','world_preview'])]
    assert not bad,bad
    write(HERE/'pck-audit.json',{'entries':pck['entries'],'forbidden_matches':bad,'success':True})
    shutil.copytree(Path(read(OLD41/'build.json')['exe']).parent/'credits',OUT/'credits')
    (OUT/'RUN.ko.md').write_text('# 잿빛 회랑 · 후보42\n\nAshenCloister-Chapter1.exe를 실행하세요. Actor42 중복 애니메이션 작업 생략 후보이며 HUD41과 FX39를 유지합니다. WASD/좌클릭 이동, Space 회피, Q 회복약, I 장비, Esc 정지. 현재41 진행을 별도42 저장 공간에 최초 한 번 복사했고 이후 진행은 독립입니다. 기존37/38/40/41 실행본과 저장은 보존했습니다. 초상은 AI 생성 2D 메뉴 원화이며 현재3D 모델 교체가 아닙니다. 최종 성능·전체 수동 완주·음향 승인은 별도입니다.\n',encoding='utf-8')
    write(HERE/'build.json',{'exe':str(exe),'sha256':sha(exe),'bytes':exe.stat().st_size,'runtime_count':176,'stage_count':178,'pck_count':len(packed),'scope':'Actor42 + HUD41/FX39 package; no full performance/manual completion claim'})
    print(json.dumps(read(HERE/'build.json')))
def verify():
    no_games();pins=read(HERE/'PRESERVED.json');preserve(pins)
    frozen=read(HERE/'FINAL-SOURCE-FREEZE.json');check(ROOT,frozen)
    stagepins=read(HERE/'staging-manifest.json');check(STAGE,stagepins)
    exe=Path(read(HERE/'build.json')['exe'])
    assert sha(exe)==read(HERE/'build.json')['sha256']
    native=HERE/'native01';assert not native.exists();native.mkdir()
    execute('packaged-integration',[exe,'--position','20,20','--script',HERE/'packaged42_integration.gd','--','--ui42-output='+str(native)],timeout=120)
    result=read(native/'PACKAGED-INTEGRATION.json');assert result['success'] is True
    write(HERE/'PACKAGED-INTEGRATION.json',result)
    preserve(pins);check(ROOT,frozen);check(STAGE,stagepins)
    write(HERE/'FINAL-PRESERVATION.json',{'success':True,'preserved_previous_builds':True,'source42_and_stage42_unchanged':True,'user37_count':len(pins['user37']),'user38_count':len(pins['user38']),'user40_count':len(pins['user40']),'user41_count':len(pins['user41']),'user42_count':len(pins['user42']),'profiles_byte_identical':True})
    print(json.dumps({'integration':result['success'],'checks':len(result['checks']),'previous_and_fork_profiles_unchanged':True}))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','adopt','build','audit','verify']);parser.add_argument('--root-go',action='store_true');action=parser.parse_args().action
    if action!='prepare':assert parser.parse_args().root_go,'Explicit root GO required; preparation is read-only'
    {'prepare':prepare,'adopt':adopt,'build':build,'audit':audit,'verify':verify}[action]()
