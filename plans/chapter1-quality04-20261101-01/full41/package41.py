"""Candidate41 explicit closure package. Adoption/build require root's later GO.

prepare only reads source facts; it never imports, exports, forks saves or adopts.
All generated evidence uses exclusive writes and unique41 destinations.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, re, shutil, subprocess, sys
sys.dont_write_bytecode=True
ROOT=Path('C:/Project/d2r-combat-baseline')
HERE=Path(__file__).resolve().parent
OLD40=HERE.parent/'full40'
OLD38=HERE.parent/'ui38/package38'
OLD37=HERE.parent/'full37'
ID='chapter1-full-candidate-20261112-41'
STAGE=Path('C:/Project/game-research/build-staging')/(ID+'-attempt02')
OUT=ROOT/'builds/chapter1'/(ID+'-attempt02')
BACKUP=Path('C:/Project/game-research/implementation-backups/chapter1-before41-20261112-01')
USER37=Path(os.environ['APPDATA'])/'AshenCloisterChapterOneQuality37'
USER38=Path(os.environ['APPDATA'])/'AshenCloisterChapterOneQuality38'
USER40=Path(os.environ['APPDATA'])/'AshenCloisterChapterOneQuality40'
USER41=Path(os.environ['APPDATA'])/'AshenCloisterChapterOneQuality41'
ENGINE=Path('C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe')
NEW=['chapter1/view/ui41/chapter_hud_quality41.gd',
     'chapter1/art/portrait41/oath_witch_portrait_v01.png',
     'chapter1/art/portrait41/ATTRIBUTION.ko.md']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,value):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def check(base,pins):
    bad=[p for p,h in pins.items() if not (base/p).is_file() or sha(base/p)!=h]
    assert not bad,{'base':str(base),'mismatches':bad}
def files():
    paths=read(OLD40/'closure.json')['runtime_source_files']+NEW
    assert len(paths)==175 and len(set(paths))==175
    assert all((ROOT/p).is_file() for p in paths)
    return sorted(paths)
def profiles(folder):
    paths=[folder/'chapter-one-profile-v1.json']+sorted(folder.glob('chapter-one-profile-v1.revision-*.json'))
    assert all(p.is_file() for p in paths),str(folder)
    return {str(p):sha(p) for p in paths}
def no_games():
    result=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object {$_.Name -like 'Godot*' -or $_.Name -like 'AshenCloister*'} | Select-Object -ExpandProperty ProcessId"],capture_output=True,text=True,check=True)
    assert not result.stdout.strip(),{'active_game_or_engine':result.stdout}
def preserve(pins,include41=True):
    check(Path('.'),pins['absolute'])
    for stage in pins['stages']:check(Path(stage['path']),stage['files'])
    check(ROOT,pins['unchanged_root40'])
    for number,folder in [(37,USER37),(38,USER38),(40,USER40)]:
        assert profiles(folder)==pins['user'+str(number)],'Current progress changed; preserve and stop: '+str(number)
    if include41:assert profiles(USER41)==pins['user41'],'Fork41 progress changed; preserve and stop'
    first_path=HERE/'ATTEMPT01-PRESERVED.json'
    if first_path.exists():
        first=read(first_path);check(Path(first['stage']),first['stage_files'])
        assert sha(first['exe'])==first['exe_sha256'],'Original attempt01 EXE changed'
        check(Path('.'),first['relocated_proof_hashes'])
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
    print(json.dumps({'build_id':ID,'runtime_count':len(files()),'stage_count':len(files())+2,'new_files':NEW,'stage':str(STAGE),'output':str(OUT),'proof':str(HERE),'backup':str(BACKUP),'user41':str(USER41),'adoption_or_fork_or_engine_started':False},ensure_ascii=False))
def adopt():
    no_games()
    assert not any(p.exists() for p in [BACKUP,USER41,STAGE,OUT]),'All41 destination directories must initially be absent'
    assert not any((HERE/p).exists() for p in ['ADOPTION.json','PRESERVED.json','SOURCE-BEFORE.json','FINAL-SOURCE-FREEZE.json','USER-FORK.json']),'41 adoption evidence already exists; never overwrite'
    freeze40=read(OLD40/'FINAL-SOURCE-FREEZE.json');check(ROOT,freeze40)
    absolute={};stages=[]
    for folder in [OLD40,OLD38,OLD37/'build']:
        freeze_path=OLD37/'FINAL-SOURCE-FREEZE.json' if folder==OLD37/'build' else folder/'FINAL-SOURCE-FREEZE.json'
        for p in [freeze_path,folder/'closure.json',folder/'staging-manifest.json',folder/'build.json']:absolute[str(p)]=sha(p)
        closure=read(folder/'closure.json');stagepins=read(folder/'staging-manifest.json');stage=Path(closure['stage']);check(stage,stagepins)
        build=read(folder/'build.json');assert sha(build['exe'])==build['sha256']
        absolute[build['exe']]=build['sha256'];stages.append({'path':str(stage),'files':stagepins})
    userpins={str(number):profiles(folder) for number,folder in [(37,USER37),(38,USER38),(40,USER40)]}
    current=read(USER40/'chapter-one-profile-v1.json')
    assert current['schema_version']==1 and len(current['items'])<=325
    before={p:sha(ROOT/p) for p in files()+['project.godot','export_presets.cfg']}
    BACKUP.mkdir()
    write(BACKUP/'FULL-ROOT-CLOSURE-BEFORE.json',before)
    for p in ['chapter1/chapter_one_view.gd','project.godot','export_presets.cfg']+NEW:
        target=BACKUP/'source'/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/p,target)
    shutil.copy2(OLD40/'FINAL-SOURCE-FREEZE.json',BACKUP/'ORIGINAL40-FREEZE.json')
    for number,pins_ in userpins.items():
        snapshot=BACKUP/('user'+number+'-readonly-snapshot');snapshot.mkdir()
        for source,h in pins_.items():
            body=Path(source).read_bytes();assert hashlib.sha256(body).hexdigest()==h
            target=snapshot/Path(source).name
            with target.open('xb') as f:f.write(body)
            assert sha(target)==h
    USER41.mkdir();copies=[]
    for source,h in userpins['40'].items():
        body=Path(source).read_bytes();assert hashlib.sha256(body).hexdigest()==h
        target=USER41/Path(source).name
        with target.open('xb') as f:f.write(body)
        assert sha(target)==h
        copies.append({'source':source,'target':str(target),'sha256':h})
    pins={'absolute':absolute,'stages':stages,'unchanged_root40':{p:h for p,h in freeze40.items() if p!='chapter1/chapter_one_view.gd'},'user41':profiles(USER41)}
    pins.update({'user'+number:pins_ for number,pins_ in userpins.items()})
    preserve(pins)
    write(HERE/'PRESERVED.json',pins)
    write(HERE/'USER-FORK.json',{'mode':'One-time byte-identical CURRENT40 main and all revision journals into initially absent41; no rewrite/reset/award/persist','copies':copies,'source_summary':{'revision':current['revision'],'items':len(current['items']),'equipped':current['equipped'],'completed_runs':current['completed_runs']}})
    assembly=ROOT/'chapter1/chapter_one_view.gd';body=assembly.read_bytes()
    old=b'res://chapter1/view/ui40/chapter_hud_quality40.gd';new=b'res://chapter1/view/ui41/chapter_hud_quality41.gd'
    assert body.count(old)==1;assembly.write_bytes(body.replace(old,new))
    after={p:sha(ROOT/p) for p in before}
    assert [p for p in before if before[p]!=after[p]]==['chapter1/chapter_one_view.gd']
    write(HERE/'SOURCE-BEFORE.json',before);write(HERE/'FINAL-SOURCE-FREEZE.json',after)
    write(HERE/'ADOPTION.json',{'root_approved':True,'backup':str(BACKUP),'runtime_count':175,'new_files':{p:after[p] for p in NEW},'changed_existing_files':['chapter1/chapter_one_view.gd'],'core_data_audio_models_fx39_unchanged':True,'preserved40_freeze':str(OLD40/'FINAL-SOURCE-FREEZE.json')})
    preserve(pins)
    print(json.dumps({'adopted':True,'profile41_forked':len(copies),'runtime':175}))
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
    project=project.replace('config/name="D2R Combat Baseline"','config/name="Ashen Cloister ChapterOne Quality41"\nconfig/use_custom_user_dir=true\nconfig/custom_user_dir_name="AshenCloisterChapterOneQuality41"')
    project=project.replace('[rendering]','[rendering]\nanti_aliasing/quality/msaa_3d=2')
    (STAGE/'project.godot').write_text(project,encoding='utf-8')
    oldstage=Path(read(OLD40/'closure.json')['stage'])
    preset=(oldstage/'export_presets.cfg').read_text(encoding='utf-8').replace('ChapterOne Quality40 Windows','ChapterOne Quality41 Windows')
    # Godot's selected resource list does not include new non-resource MD.
    # Include this exact authored attribution, not every research/document file.
    assert preset.count('include_filter="')==1
    preset=preset.replace('include_filter="','include_filter="chapter1/art/portrait41/ATTRIBUTION.ko.md,',1)
    marker='export_files=PackedStringArray(';assert preset.count(marker)==1
    preset=preset.replace(marker,marker+', '.join(json.dumps('res://'+p) for p in NEW)+', ')
    (STAGE/'export_presets.cfg').write_text(preset,encoding='utf-8')
    stagepins={p:sha(STAGE/p) for p in files()+['project.godot','export_presets.cfg']}
    write(HERE/'staging-manifest.json',stagepins)
    write(HERE/'closure.json',{'build_id':ID,'runtime_source_files':files(),'source_count':175,'stage_count':177,'stage':str(STAGE),'output':str(OUT),'scope':'Menu portrait UI41 on HUD40+FX39; Core37/World37c/Actor36/Input21/audio/models unchanged'})
    execute('import',[ENGINE,'--headless','--path',STAGE,'--editor','--import','--quit'])
    exe=OUT/'AshenCloister-Chapter1.exe'
    execute('export',[ENGINE,'--headless','--path',STAGE,'--export-release','ChapterOne Quality41 Windows',exe])
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
    bad=[p for p in packed if any(term in p.lower() for term in ['plans/','research/','tests/','tools/','evidence/','baseline.tscn','ui38_probe','ui40_probe','ui41_probe','packaged40_integration','packaged41_integration','frost39_compare','world_preview'])]
    assert not bad,bad
    write(HERE/'pck-audit.json',{'entries':pck['entries'],'forbidden_matches':bad,'success':True})
    shutil.copytree(Path(read(OLD40/'build.json')['exe']).parent/'credits',OUT/'credits')
    shutil.copy2(ROOT/'chapter1/art/portrait41/ATTRIBUTION.ko.md',OUT/'credits/AI-PORTRAIT41-ATTRIBUTION.ko.md')
    (OUT/'RUN.ko.md').write_text('# 잿빛 회랑 · 후보41\n\nAshenCloister-Chapter1.exe를 실행하세요. 서약 원화와 실제 첫 기술 정보를 넣은 메뉴, 보관함·구역 안내·결과 UI와 냉기 표현 개선본입니다. WASD/좌클릭 이동, Space 회피, Q 회복약, I 장비, Esc 정지. 현재40 진행을 별도41 저장 공간에 최초 한 번 복사했고 이후 진행은 독립입니다. 기존37/38/40 실행본과 저장은 보존했습니다. 초상은 AI 생성 2D 메뉴 원화이며 현재3D 모델 교체가 아닙니다. 최종 성능·전체 수동 완주·음향 승인은 별도입니다.\n',encoding='utf-8')
    write(HERE/'build.json',{'exe':str(exe),'sha256':sha(exe),'bytes':exe.stat().st_size,'runtime_count':175,'stage_count':177,'pck_count':len(packed),'scope':'UI41 menu portrait + HUD40/FX39 package; no full performance/manual completion claim'})
    print(json.dumps(read(HERE/'build.json')))
def verify():
    no_games();pins=read(HERE/'PRESERVED.json');preserve(pins)
    frozen=read(HERE/'FINAL-SOURCE-FREEZE.json');check(ROOT,frozen)
    stagepins=read(HERE/'staging-manifest.json');check(STAGE,stagepins)
    exe=Path(read(HERE/'build.json')['exe'])
    assert sha(exe)==read(HERE/'build.json')['sha256']
    native=HERE/'native01';assert not native.exists();native.mkdir()
    execute('packaged-integration',[exe,'--position','20,20','--script',HERE/'packaged41_integration.gd','--','--ui41-output='+str(native)],timeout=120)
    result=read(native/'PACKAGED-INTEGRATION.json');assert result['success'] is True
    write(HERE/'PACKAGED-INTEGRATION.json',result)
    preserve(pins);check(ROOT,frozen);check(STAGE,stagepins)
    write(HERE/'FINAL-PRESERVATION.json',{'success':True,'preserved_previous_builds':True,'source41_and_stage41_unchanged':True,'user37_count':len(pins['user37']),'user38_count':len(pins['user38']),'user40_count':len(pins['user40']),'user41_count':len(pins['user41']),'profiles_byte_identical':True})
    print(json.dumps({'integration':result['success'],'checks':len(result['checks']),'previous_and_fork_profiles_unchanged':True}))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','adopt','build','audit','verify']);action=parser.parse_args().action
    {'prepare':prepare,'adopt':adopt,'build':build,'audit':audit,'verify':verify}[action]()
