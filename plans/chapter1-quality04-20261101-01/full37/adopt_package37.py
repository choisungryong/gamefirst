"""Draft37: explicit adoption and build are separate; importing this file has no writes."""
from pathlib import Path
import argparse,csv,hashlib,importlib.util,json,shutil,subprocess,sys
sys.dont_write_bytecode=True
ROOT=Path('C:/Project/d2r-combat-baseline')
HERE=Path(__file__).resolve().parent
PREVIOUS=HERE.parent/'full36'
STUDY=HERE.parent/'masonry37'
BACKUP=Path('C:/Project/game-research/implementation-backups/chapter1-before37-20261106-01')
SOURCE_USER=Path.home()/'AppData/Roaming/AshenCloisterChapterOneQuality36'
NEW_USER=Path.home()/'AppData/Roaming/AshenCloisterChapterOneQuality37'
NEW_FILES=['chapter1/core/chapter_run_quality37.gd','chapter1/core/run_growth_quality37.gd','chapter1/data/growth_quality37.json','chapter1/view/chapter_world_quality37.gd','chapter1/view/chapter_world_quality37b.gd','chapter1/view/chapter_world_quality37c.gd','chapter1/view/chapter_masonry_quality37c.gdshader']
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path,value):
    path=Path(path);assert not path.exists(),f'Preserve evidence: {path}'
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,ensure_ascii=False);f.write('\n')
def check(base,pins):
    bad=[name for name,value in pins.items() if not (base/name).is_file() or sha(base/name)!=value]
    assert not bad,{'base':str(base),'mismatches':bad}
def package():
    spec=importlib.util.spec_from_file_location('draft37_package',HERE/'package_full37.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
def no_game_processes():
    result=subprocess.run(['tasklist','/fo','csv','/nh'],capture_output=True,text=True,check=True)
    names=[row[0] for row in csv.reader(result.stdout.splitlines()) if row]
    active=[name for name in names if 'godot' in name.lower() or 'ashencloister' in name.lower()]
    assert not active,{'stop_existing_game_or_engine_before_adoption':active}
def preflight(cost_proof,review_proof):
    no_game_processes()
    p=package()
    assert len(p.paths())==163
    assert not any(path.exists() for path in (BACKUP,NEW_USER,HERE/'ADOPTION.json',HERE/'FINAL-SOURCE-FREEZE.json',p.STAGE,p.OUTPUT,p.PROOF)),'New backup/user37/stage/output/evidence must be absent; no overwrite or retry in place'
    check(ROOT,read(PREVIOUS/'FINAL-SOURCE-FREEZE.json'))
    old_stage=Path(read(PREVIOUS/'build/closure.json')['stage'])
    old_stage_pins=read(PREVIOUS/'build/staging-manifest.json')
    assert len(old_stage_pins)==158
    check(old_stage,old_stage_pins)
    users=read(PREVIOUS/'USER-PRESERVATION-ADDENDUM02.json')['user_pins']
    assert len(users)==9;check(Path('.'),users)
    old=read(PREVIOUS/'ADOPTION.json')['preserved_exes']
    build=read(PREVIOUS/'build/build.json')
    old[str(Path(build['exe']).relative_to(ROOT)).replace('\\','/')]=build['sha256']
    check(ROOT,old)
    visual=read(STUDY/'compare05/COMPARISON.json')
    assert all(visual['checks'].values())
    visual_source=read(STUDY/'compare05/SOURCE.json')['pins']
    for name in NEW_FILES[3:]:assert sha(ROOT/name)==visual_source[name.replace('/','\\')],name
    assert read(STUDY/'text02/RESULT.json')['passed']
    fixed=read(STUDY/'text02/PRESERVATION.json')['fixed_successor_sha256']
    assert sha(ROOT/'chapter1/core/run_growth_quality37.gd')==fixed
    text_review=read(STUDY/'text02/independent-review.json')
    assert text_review['source_sha256']==fixed and all(text_review['checks'].get(k) is True for k in ('execution_exit0','stderr_actual_bytes0','result_passed','current_source_matches_launch'))
    original_text=read(STUDY/'text01/PRESERVATION.json')['new_source_hashes']
    for name in NEW_FILES[:3]:
        if name!='chapter1/core/run_growth_quality37.gd':assert sha(ROOT/name)==original_text[name],name
    cost=read(cost_proof)
    assert all(cost['checks'].get(k) is True for k in ('same_complete_core','same_settings','actual1080p','both_focused'))
    review=read(review_proof)
    assert review.get('approved') is True,'Independent package review must explicitly approve'
    helper_names=['package_full37.py','adopt_package37.py','release_behavior37_probe.gd']
    assert set(review['helper_sha256'])==set(helper_names),'Independent review must pin all3helpers'
    for name in helper_names:assert sha(HERE/name)==review['helper_sha256'][name],{'reviewed_helper_changed':name}
    profile=read(SOURCE_USER/'chapter-one-profile-v1.json')
    assert profile['schema_version']==1 and profile['revision']==2 and len(profile['items'])==22 and profile['completed_runs']==1 and profile['equipped']=={'body':1}
    source_profiles={name:value for name,value in users.items() if Path(name).parent==SOURCE_USER}
    assert len(source_profiles)==3
    assert shutil.disk_usage(ROOT).free>=500*1024*1024,'Need500MiB free minimum for~250MiB isolated package plus margin'
    return p,users,old,source_profiles
def adopt(cost_proof,review_proof,root_approved):
    assert root_approved,'Root must review exclusive cost variance and independent review before explicit adoption'
    p,users,old,source_profiles=preflight(cost_proof,review_proof)
    before=read(PREVIOUS/'FINAL-SOURCE-FREEZE.json')
    BACKUP.mkdir()
    backed={}
    for name in ['chapter1/chapter_one_view.gd','project.godot','export_presets.cfg']:
        target=BACKUP/'source'/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,target);backed[name]=sha(target)
    write(BACKUP/'SOURCE-BEFORE.json',before)
    shutil.copy2(PREVIOUS/'FINAL-SOURCE-FREEZE.json',BACKUP/'root36-FINAL-SOURCE-FREEZE.json')
    shutil.copy2(PREVIOUS/'USER-PRESERVATION-ADDENDUM02.json',BACKUP/'USER-PRESERVATION-ADDENDUM02.json')
    for name,value in users.items():
        source=Path(name);target=BACKUP/'user-profiles'/source.parent.name/source.name
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        assert sha(target)==value
    write(BACKUP/'MANIFEST.json',{'backed_source':backed,'root36_source_before':before,'user_pins_before':users,'preserved_exes':old,'scope':'Only3rootfiles and9smallprofiles copied; original158source closure remains in preserved36stage+manifest. No full repo copy.'})
    NEW_USER.mkdir()
    copies=[]
    for name,value in source_profiles.items():
        source=Path(name);target=NEW_USER/source.name
        with target.open('xb') as f:f.write(source.read_bytes())
        assert sha(target)==value
        users[str(target)]=value
        copies.append({'source':str(source),'copy':str(target),'sha256':value,'bytes':target.stat().st_size})
    assert len(users)==12 and read(NEW_USER/'chapter-one-profile-v1.json')==read(SOURCE_USER/'chapter-one-profile-v1.json')
    write(HERE/'USER-CONTINUITY.json',{'mode':'Explicit one-time byte-identical fork into initially absent Quality37; no schema rewrite/grant/_persist or old profile edit','copies':copies,'source_profile_before':read(SOURCE_USER/'chapter-one-profile-v1.json'),'native_ui_confirmation_pending':True})
    source=ROOT/'chapter1/chapter_one_view.gd'
    body=source.read_bytes()
    for old_ref,new_ref in [('chapter_run_quality36.gd','chapter_run_quality37.gd'),('chapter_world_quality31d.gd','chapter_world_quality37c.gd')]:
        old_ref=old_ref.encode('utf-8');new_ref=new_ref.encode('utf-8')
        assert body.count(old_ref)==1;body=body.replace(old_ref,new_ref)
    source.write_bytes(body)
    assert sha(ROOT/'project.godot')==before['project.godot'] and sha(ROOT/'export_presets.cfg')==before['export_presets.cfg']
    check(Path('.'),users);check(ROOT,old)
    write(HERE/'SOURCE-BEFORE.json',before)
    write(HERE/'ADOPTION.json',{'backup':str(BACKUP),'backed_source':backed,'preserved_freeze36':{'path':str(PREVIOUS/'FINAL-SOURCE-FREEZE.json'),'copy':str(BACKUP/'root36-FINAL-SOURCE-FREEZE.json'),'sha256':sha(PREVIOUS/'FINAL-SOURCE-FREEZE.json')},'preserved_stage36':{'path':read(PREVIOUS/'build/closure.json')['stage'],'pins':read(PREVIOUS/'build/staging-manifest.json'),'manifest_path':str(PREVIOUS/'build/staging-manifest.json'),'manifest_sha256':sha(PREVIOUS/'build/staging-manifest.json')},'preserved_exes':old,'user_pins':users,'tested_source':{name:sha(ROOT/name) for name in NEW_FILES},'helper_pins':{name:sha(HERE/name) for name in ['package_full37.py','adopt_package37.py','release_behavior37_probe.gd']},'cost_proof':{'path':str(cost_proof),'sha256':sha(cost_proof),'scope':'Root explicitly accepted single static pair variance; not final dynamic performance'},'independent_review':{'path':str(review_proof),'sha256':sha(review_proof)},'root_explicit_adoption_approved':True,'scope':p.SCOPE})
    p.freeze(HERE/'FINAL-SOURCE-FREEZE.json')
    write(HERE/'SOURCE-AFTER.json',read(HERE/'FINAL-SOURCE-FREEZE.json'))
    write(HERE/'USER-PRESERVATION-ADDENDUM01.json',{'user_pins':users,'reason':'Latest9original23/29/36 pins plus3byte-identical37continuitycopies; native37maylaterlegitimatelychange37only'})
    print(json.dumps({'adopted':True,'runtime163':len(p.paths()),'user_pins':len(users),'no_build_yet':True}))
def build():
    no_game_processes()
    p=package()
    assert read(HERE/'ADOPTION.json')['root_explicit_adoption_approved'] is True
    p.build(HERE/'FINAL-SOURCE-FREEZE.json')
if __name__=='__main__':
    parser=argparse.ArgumentParser();subs=parser.add_subparsers(dest='action',required=True)
    gate=subs.add_parser('adopt');gate.add_argument('--cost-proof',type=Path,required=True);gate.add_argument('--review-proof',type=Path,required=True);gate.add_argument('--root-approved',action='store_true')
    subs.add_parser('build')
    args=parser.parse_args()
    if args.action=='adopt':adopt(args.cost_proof.resolve(),args.review_proof.resolve(),args.root_approved)
    else:build()
