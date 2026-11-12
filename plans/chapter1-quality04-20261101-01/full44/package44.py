"""Arc44 package, explicit source closure, reversible adoption and save fork."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OLD=HERE.parent/'full43'
ID='chapter1-full-candidate-20261113-44'
STAGE=Path('C:/Project/game-research/build-staging')/ID
OUT=ROOT/'builds/chapter1'/ID
BACKUP=Path('C:/Project/game-research/implementation-backups/chapter1-before44-20261113-01')
USER43=Path(os.environ['APPDATA'])/'AshenCloisterChapterOneQuality43'
USER44=Path(os.environ['APPDATA'])/'AshenCloisterChapterOneQuality44'
NEW=['chapter1/view/chapter_elements_quality44.gd']+['chapter1/view/arc_'+n+'_quality44.gdshader' for n in ['core','contact']]
ASSEMBLY='chapter1/chapter_one_view.gd'
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
old=module('package42',HERE.parent/'full42/package42.py')
previous=module('final43',HERE.parent/'final-performance43/run_performance43.py')
old.HERE=HERE
sha,read,write,check,execute=old.sha,old.read,old.write,old.check,old.execute
def files():
    paths=sorted(read(OLD/'closure.json')['runtime_source_files']+NEW)
    assert len(paths)==183 and len(set(paths))==183
    return paths
def preserve(pins):
    check(ROOT,pins['unchanged_root43'])
    check(Path('.'),pins['absolute'])
    for stage in pins['stages']:check(Path(stage['path']),stage['files'])
    assert previous.current_profiles()==pins['profiles'],'Current user progress changed; never restore old saves'
def adopt():
    old.no_games()
    assert not any(p.exists() for p in [STAGE,OUT,USER44,BACKUP])
    assert not (HERE/'FINAL-SOURCE-FREEZE.json').exists()
    selection=read(HERE/'SELECTION.json')
    assert selection['visual_review_passed'] and selection['parity_passed']
    check(ROOT,selection['files'])
    snapshot=previous.package_snapshot()
    freeze=read(OLD/'FINAL-SOURCE-FREEZE.json');check(ROOT,freeze)
    absolute=dict(snapshot['manifest_sha256'])
    absolute[str(old.ROOT/'builds/chapter1/chapter1-full-candidate-20261113-43/AshenCloister-Chapter1.exe')]=snapshot['exe_sha256']
    stages=[{'path':snapshot['stage'],'files':read(OLD/'staging-manifest.json')}]
    for p in snapshot['previous_packages'].values():
        absolute[p['exe']]=p['sha256'];stages.append({'path':p['stage'],'files':p['stage_pins']})
        manifests=p.get('manifest_sha256')
        if isinstance(manifests,dict):absolute.update(manifests)
    original41=HERE.parent/'full41/ATTEMPT01-PRESERVED.json'
    absolute[str(original41)]=sha(original41)
    BACKUP.mkdir();shutil.copy2(ROOT/ASSEMBLY,BACKUP/'chapter_one_view.gd')
    write(BACKUP/'ROOT43-BEFORE.json',freeze)
    write(BACKUP/'PROFILES-BEFORE.json',snapshot['user_pins'])
    USER44.mkdir()
    for source in USER43.glob('chapter-one-profile-v1*.json'):
        assert str(source.resolve()) in snapshot['user_pins']
        target=USER44/source.name
        with target.open('xb') as output:output.write(source.read_bytes())
        assert sha(target)==snapshot['user_pins'][str(source.resolve())]
    assert (USER44/'chapter-one-profile-v1.json').is_file()
    pins={'unchanged_root43':{p:h for p,h in freeze.items() if p!=ASSEMBLY},'absolute':absolute,'stages':stages,'profiles':previous.current_profiles()}
    # The new fork is additional; every pre-existing profile must remain unchanged.
    check(Path('.'),snapshot['user_pins'])
    preserve(pins);write(HERE/'PRESERVED.json',pins)
    p=ROOT/ASSEMBLY;body=p.read_bytes()
    source=b'res://chapter1/view/chapter_elements_quality43.gd'
    target=b'res://chapter1/view/chapter_elements_quality44.gd'
    assert body.count(source)==1;p.write_bytes(body.replace(source,target))
    frozen={p:sha(ROOT/p) for p in files()+['project.godot','export_presets.cfg']}
    write(HERE/'FINAL-SOURCE-FREEZE.json',frozen)
    write(HERE/'ADOPTION.json',{'backup':str(BACKUP),'changed_existing_files':[ASSEMBLY],'runtime_count':183,'current43_forked_once':True,'new_files':NEW})
    preserve(pins);print('ADOPTED44',flush=True)
def build():
    old.no_games();pins=read(HERE/'PRESERVED.json');preserve(pins)
    frozen=read(HERE/'FINAL-SOURCE-FREEZE.json');check(ROOT,frozen)
    assert not STAGE.exists() and not OUT.exists()
    STAGE.mkdir();OUT.mkdir(parents=True)
    for name in files():
        target=STAGE/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
    oldstage=Path(read(OLD/'closure.json')['stage'])
    p=(oldstage/'project.godot').read_text(encoding='utf-8-sig').replace('Quality43','Quality44')
    (STAGE/'project.godot').write_text(p,encoding='utf-8')
    preset=(oldstage/'export_presets.cfg').read_text(encoding='utf-8-sig').replace('ChapterOne Quality43 Windows','ChapterOne Quality44 Windows')
    marker='export_files=PackedStringArray(';assert preset.count(marker)==1
    preset=preset.replace(marker,marker+', '.join(json.dumps('res://'+p) for p in NEW)+', ')
    assert 'chapter1/art/portrait41/ATTRIBUTION.ko.md' in preset.split('include_filter="',1)[1].split('"',1)[0].split(',')
    (STAGE/'export_presets.cfg').write_text(preset,encoding='utf-8')
    stagepins={p:sha(STAGE/p) for p in files()+['project.godot','export_presets.cfg']}
    write(HERE/'staging-manifest.json',stagepins)
    write(HERE/'closure.json',{'build_id':ID,'runtime_source_files':files(),'source_count':183,'stage_count':185,'stage':str(STAGE),'output':str(OUT),'scope':'Arc44 two shader replacements; Fire43/Actor42/HUD41/Core37/cold39/audio/models unchanged'})
    execute('import',[old.ENGINE,'--headless','--path',STAGE,'--editor','--import','--quit'])
    exe=OUT/'AshenCloister-Chapter1.exe'
    execute('export',[old.ENGINE,'--headless','--path',STAGE,'--export-release','ChapterOne Quality44 Windows',exe])
    parser=module('pck_parser43',ROOT/'tools/build_phase7.py');packed={r['path'].removeprefix('res://'):r for r in parser.pck_entries(exe)['entries']}
    for p in files():
        extension=Path(p).suffix
        expected=p+'.import' if extension in ['.png','.wav','.glb','.svg'] else p+'.remap' if extension in ['.gd','.tscn'] else p
        assert expected in packed or extension=='.gdshader' and p+'.remap' in packed,('Missing dependency',p)
        if extension in ['.json','.txt','.md']:assert packed[p]['sha256']==frozen[p]
    bad=[p for p in packed if any(part in p.lower() for part in ['plans/','research/','tests/','tools/','evidence/','baseline.tscn'])]
    assert not bad
    write(HERE/'pck-audit.json',{'success':True,'entries':list(packed.values()),'forbidden_matches':bad})
    shutil.copytree(Path(read(OLD/'build.json')['exe']).parent/'credits',OUT/'credits')
    write(HERE/'build.json',{'exe':str(exe),'sha256':sha(exe),'bytes':exe.stat().st_size,'runtime_count':183,'stage_count':185,'pck_count':len(packed),'scope':'Arc44 presentation; final performance/full manual completion separate'})
    check(ROOT,frozen);check(STAGE,stagepins);preserve(pins)
    print(json.dumps(read(HERE/'build.json')),flush=True)
def verify():
    old.no_games();pins=read(HERE/'PRESERVED.json');preserve(pins)
    frozen=read(HERE/'FINAL-SOURCE-FREEZE.json');check(ROOT,frozen)
    stagepins=read(HERE/'staging-manifest.json');check(STAGE,stagepins)
    build=read(HERE/'build.json');assert sha(build['exe'])==build['sha256']
    output=HERE/'native01';assert not output.exists();output.mkdir()
    execute('packaged-integration',[build['exe'],'--position','20,20','--script',HERE/'packaged44_integration.gd','--','--ui44-output='+str(output)],timeout=120)
    result=read(output/'PACKAGED-INTEGRATION.json');assert result['success']
    write(HERE/'PACKAGED-INTEGRATION.json',result)
    check(ROOT,frozen);check(STAGE,stagepins);preserve(pins)
    write(HERE/'FINAL-PRESERVATION.json',{'success':True,'preserved_previous_builds':True,'source44_and_stage44_unchanged':True,'profiles_byte_identical':True,'profiles_count':len(pins['profiles'])})
    print(json.dumps({'integration':True,'checks':len(result['checks']),'preserved':True}),flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','adopt','build','verify']);args=parser.parse_args()
    if args.action=='prepare':print(json.dumps({'runtime_count':len(files()),'stage_count':185,'stage':str(STAGE),'adopted':False}))
    else:{'adopt':adopt,'build':build,'verify':verify}[args.action]()
