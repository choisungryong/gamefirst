"""Immutable full candidate21 workflow. prepare does not stage, import, export, or run GPU.
Freeze only after all source owners finish. build requires the exact frozen closure.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re,shutil,subprocess,sys
sys.dont_write_bytecode=True
ROOT=Path('C:/Project/d2r-combat-baseline')
HERE=Path(__file__).resolve().parent
ID='chapter1-full-candidate-20261103-21'
STAGE=Path('C:/Project/game-research/build-staging')/ID
OUTPUT=ROOT/'builds/chapter1'/ID
PROOF=HERE/'build'
ENGINE=Path('C:/Project/rea-tools/godot-4.5.1/Godot_v4.5.1-stable_win64_console.exe')
OLD=ROOT/'plans/chapter1-quality-20261031-01/package03/build'
BACKUP=Path('C:/Project/game-research/implementation-backups/chapter1-quality04-before-20261101-01')
EXTRAS=['chapter1/presentation/frame_probe.gd', 'chapter1/view/hero_occlusion_rim.gdshader', 'chapter1/ChapterOne.tscn', 'chapter1/chapter_one_view.gd', 'chapter1/core/chapter_items.gd', 'chapter1/core/chapter_profile.gd', 'chapter1/core/chapter_run.gd', 'chapter1/core/chapter_pilot.gd', 'chapter1/view/chapter_effects.gd', 'chapter1/view/chapter_hud.gd', 'chapter1/view/chapter_world.gd', 'chapter1/view/chapter_ground.gdshader', 'chapter1/view/chapter_actors.gd','chapter1/view/rigged_hero_actors.gd','chapter1/view/ember_staff_visual.gd','chapter1/art/rigged_mage/v01/mage_animated.glb','chapter1/art/rigged_mage/v01/ATTRIBUTION.ko.md','chapter1/view/chapter_world_quality10.gd','chapter1/view/chapter_grass_quality10.gdshader','chapter1/view/chapter_ground_quality10.gdshader','chapter1/view/chapter_effects_quality10.gd','chapter1/view/contact_quality10.gdshader','chapter1/view/chapter_actors_quality12.gd','chapter1/art/chained_warden/v01/chained_demon_animated.glb','chapter1/art/chained_warden/v01/ATTRIBUTION.ko.md','chapter1/view/chapter_elements_quality14.gd','chapter1/view/comet_quality14.gdshader','chapter1/view/impact_quality14.gdshader','chapter1/view/arc_quality14.gdshader','chapter1/core/chapter_run_quality16.gd','chapter1/view/chapter_elements_quality16.gd','chapter1/view/chapter_hud_quality16.gd','chapter1/view/chapter_actors_quality16.gd','chapter1/view/chapter_hud_quality17.gd','chapter1/view/equipment_sigil_quality17.gd','chapter1/view/chapter_actors_quality17.gd','chapter1/view/chapter_world_quality17.gd','chapter1/view/chapter_world_quality18.gd','chapter1/view/chapter_actors_demon19.gd','chapter1/view/chapter_actors_readable19.gd','chapter1/view/chapter_actors_batched19.gd','chapter1/view/chapter_hud_quality20.gd','chapter1/view/chapter_actors_quality20.gd','chapter1/view/chapter_elements_quality20.gd','chapter1/view/chapter_actors_quality21.gd','chapter1/chapter_one_input21.gd']
SCOPE='Full chapter candidate21: rigged ranged/charger roles, shared single-surface staff, paid dash/recovery and bounded distant pose updates. Full-chapter click target uses unlocked core bounds, fixing later-zone first-arena clamp. Core16/World18/HUD20/FX20 unchanged. Not final art/manual/audio/save-path/formal performance approval.'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):
    p=Path(p);assert not p.exists(),f'Preserve existing evidence: {p}'
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,ensure_ascii=False);f.write('\n')
def paths():
    old=read(OLD/'closure.json')['runtime_source_files']
    assert len(old)==70 and len(set(old))==70
    result=sorted(old+EXTRAS)
    assert len(set(result))==116 and all((ROOT/p).is_file() for p in result)
    return result
def check(base,pins):
    mismatch=[p for p,h in pins.items() if not (base/p).is_file() or sha(base/p)!=h]
    assert not mismatch,{'base':str(base),'mismatches':mismatch}
def preservation():
    backup=read(BACKUP/'manifest.json')
    checks={}
    groups={'backup77':(BACKUP/'source',{p:v['sha256'] for p,v in backup['files'].items()}),
            'old_exes3_profiles2':(ROOT,{p:v['sha256'] for p,v in backup['pinned_exes3_profiles2'].items()}),
            'candidate03_stage72':(Path('C:/Project/game-research/build-staging/chapter1-c2-candidate-20261101-03'),read(OLD/'staging-manifest.json')),
            'baseline51':(ROOT,read(ROOT/'evidence/phase7/builds/phase7-candidate-20261030-01/source-manifest.json'))}
    for label,(base,pins) in groups.items():
        check(base,pins);checks[label]={'count':len(pins),'mismatches':[]}
    return checks
def prepare():
    write(HERE/'PREPARATION.json',{'build_id':ID,'runtime_paths':paths(),'source_count':len(paths()),'old_closure_sha256':sha(OLD/'closure.json'),
         'extras':EXTRAS,'stage':str(STAGE),'output':str(OUTPUT),'preservation':preservation(),'provisional':True,
         'no_stage_import_export_or_gpu':True,'scope':SCOPE})
    print(json.dumps({'prepared':True,'source_count':len(paths()),'no_export_or_gpu':True}))
def freeze(destination):
    write(destination,{p:sha(ROOT/p) for p in paths()+['project.godot','export_presets.cfg']})
    print(json.dumps({'freeze':str(destination),'sha256':sha(destination)}))
def execute(label,command,timeout=300):
    result=subprocess.run([str(p) for p in command],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
    report={'command':[str(p) for p in command],'actual_exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
    write(PROOF/(label+'-execution.json'),report)
    assert result.returncode==0 and not re.search(r'(?:SCRIPT ERROR|ERROR:|Parse Error)',result.stdout+result.stderr),report
    return report
def build(frozen):
    pins=read(frozen);runtime=paths()
    assert set(pins)==set(runtime+['project.godot','export_presets.cfg'])
    check(ROOT,pins);before=preservation()
    assert not any(p.exists() for p in (STAGE,OUTPUT,PROOF)),'Unique stage/output/proof required'
    for folder in (STAGE,OUTPUT,PROOF):folder.mkdir(parents=True)
    write(PROOF/'source-manifest.json',{p:pins[p] for p in runtime})
    write(PROOF/'freeze-input.json',{'path':str(Path(frozen).resolve()),'sha256':sha(frozen)})
    for p in runtime:
        target=STAGE/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/p,target)
    project=(ROOT/'project.godot').read_text(encoding='utf-8')
    assert project.count('run/main_scene="res://Baseline.tscn"')==1
    assert project.count('config/name="D2R Combat Baseline"')==1
    project=project.replace('run/main_scene="res://Baseline.tscn"','run/main_scene="res://chapter1/ChapterOne.tscn"')
    project=project.replace('config/name="D2R Combat Baseline"','config/name="Ashen Cloister ChapterOne Quality21"\nconfig/use_custom_user_dir=true\nconfig/custom_user_dir_name="AshenCloisterChapterOneQuality21"')
    project=project.replace('[rendering]','[rendering]\nanti_aliasing/quality/msaa_3d=2')
    (STAGE/'project.godot').write_text(project,encoding='utf-8')
    resources=['res://'+p for p in runtime if Path(p).suffix in ('.gd','.gdshader','.tscn','.png','.wav','.glb')]
    preset=(ROOT/'export_presets.cfg').read_text(encoding='utf-8')
    assert preset.count('export_filter="all_resources"')==1
    assert preset.count('include_filter="assets/licenses/*.txt,game_data/*.json"')==1
    preset=preset.replace('name="Windows Desktop"','name="ChapterOne Quality21 Windows"')
    preset=preset.replace('export_filter="all_resources"','export_filter="selected_resources"\nexport_files=PackedStringArray('+', '.join(json.dumps(p) for p in resources)+')')
    preset=preset.replace('include_filter="assets/licenses/*.txt,game_data/*.json"','include_filter="chapter1/data/*.json,chapter1/art/actors/*.json,chapter1/art/quality03/*.json,chapter1/art/quality03_audio/*.json,chapter1/art/quality03_audio/LICENSE-*.txt,chapter1/art/rigged_mage/v01/*.md,chapter1/art/chained_warden/v01/*.md"')
    assert preset.count(',*.md')==1
    preset=preset.replace(',*.md','')
    (STAGE/'export_presets.cfg').write_text(preset,encoding='utf-8')
    staged={p:sha(STAGE/p) for p in runtime+['project.godot','export_presets.cfg']}
    write(PROOF/'staging-manifest.json',staged)
    write(PROOF/'closure.json',{'build_id':ID,'runtime_source_files':runtime,'source_count':len(runtime),'stage_count':len(staged),'stage':str(STAGE),'output':str(OUTPUT),'extras':EXTRAS,'scope':SCOPE})
    exe=OUTPUT/'AshenCloister-Chapter1.exe'
    execute('import',[ENGINE,'--headless','--path',STAGE,'--editor','--import'])
    execute('export',[ENGINE,'--headless','--path',STAGE,'--export-release','ChapterOne Quality21 Windows',exe])
    check(ROOT,pins);check(STAGE,staged)
    spec=importlib.util.spec_from_file_location('preserved_pck_parser',ROOT/'tools/build_phase7.py')
    parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
    package=parser.pck_entries(exe)
    packed={r['path'].removeprefix('res://'):r for r in package['entries']}
    for p in runtime:
        ext=Path(p).suffix
        expected=p+'.import' if ext in ('.png','.wav','.glb') else p+'.remap' if ext in ('.gd','.tscn') else p
        assert expected in packed or (ext=='.gdshader' and p+'.remap' in packed),'Missing dependency '+p
        if ext in ('.json','.txt','.md'):assert packed[p]['sha256']==pins[p],'Metadata differs '+p
    forbidden=('evidence/','plans/','research/','tests/','tools/','attempts/','hero_run','Baseline.tscn','baseline_view','assets/expedition/','presentation/expedition_audio')
    bad=[p for p in packed if any(term.lower() in p.lower() for term in forbidden)]
    assert not bad,bad
    package.update({'exe_sha256':sha(exe),'forbidden_matches':bad,'success':True})
    write(PROOF/'pck-audit.json',package)
    smoke=execute('packaged-headless-smoke',[exe,'--headless','--fixed-fps','60','--','--chapter1-profile-off','--chapter1-start','--chapter1-pilot','--chapter1-qa-ignore-focus','--chapter1-seed=90131','--chapter1-quit-after=30'],60)
    audio=[json.loads(s.split('CHAPTER1_AUDIO ',1)[1]) for s in smoke['stdout'].splitlines() if 'CHAPTER1_AUDIO ' in s]
    ready=[json.loads(s.split('CHAPTER1_READY ',1)[1]) for s in smoke['stdout'].splitlines() if 'CHAPTER1_READY ' in s]
    assert len(audio)==1 and not audio[0]['raw_fallbacks'] and len(ready)==1 and not ready[0]['raw_texture_fallbacks']
    write(PROOF/'imported-resource-proof.json',{'audio':audio,'ready':ready,'scope':'Headless load only; not GPU/visual/audio approval'})

    results=[json.loads(line.split('FULL_CHAPTER_RUNTIME_RESULT ',1)[1]) for line in smoke['stdout'].splitlines() if 'FULL_CHAPTER_RUNTIME_RESULT ' in line]
    assert results and results[-1]['tick']>1200 and results[-1]['growth']['level']>=2 and results[-1]['equipped'],'Release normal policy must progress and equip past the first choice'
    write(PROOF/'release-policy-smoke.json',{'result':results[-1],'scope':'30simsec fixed-fps/headless normal driver, not actual GPU/manual/performance'})
    execute('release-behavior-probe',[exe,'--headless','--script',ROOT/'plans/chapter1-quality04-20261101-01/root-resume-01/release_behavior_probe.gd'],60)

    elements=[json.loads(line.split('CHAPTER1_ELEMENTS14 ',1)[1])for line in smoke['stdout'].splitlines()if 'CHAPTER1_ELEMENTS14 'in line]
    assert len(elements)==1 and elements[0]['ice_targets_cap']==24 and elements[0]['arc_links_cap']==64
    write(PROOF/'inherited-full17-headless.json', {'source':str(HERE.parent/'full17/build'),'reason':'Actor presentation and full-chapter mouse controller changed. Full17 three-primary/full19 frost proofs preserved; unchanged16 combat simulation, no new full21 whole run claimed. Input fix separately tested.'})

    credits=OUTPUT/'credits';credits.mkdir()
    for p in runtime+['chapter1/art/ASSET-LEDGER.json','chapter1/art/quality03/ASSET-LEDGER-v04.json']:
        if Path(p).name.startswith('LICENSE-') or Path(p).name in ('AUDIO-LEDGER.json','ASSET-LEDGER.json','ASSET-LEDGER-v04.json'):shutil.copy2(ROOT/p,credits/Path(p).name)
    shutil.copy2(ROOT/'chapter1/art/rigged_mage/v01/ATTRIBUTION.ko.md',credits/'ATTRIBUTION-Rigged-Mage.ko.md')
    shutil.copy2(ROOT/'chapter1/art/chained_warden/v01/ATTRIBUTION.ko.md',credits/'ATTRIBUTION-Chained-Warden.ko.md')
    shutil.copy2(HERE/'RUN.ko.md',OUTPUT/'RUN.ko.md')
    after=preservation();assert before==after
    write(PROOF/'preservation.json',{'before':before,'after':after,'success':True,'scope':'Selected immutable backups/baseline/exes/profiles/stage pins; not every historical file'})
    write(PROOF/'build.json',{'exe':str(exe),'sha256':sha(exe),'bytes':exe.stat().st_size,'source_count':len(runtime),'stage_count':len(staged),'pck_count':len(packed),'scope':SCOPE})
    print(json.dumps(read(PROOF/'build.json')))
if __name__=='__main__':
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='action',required=True)
    sub.add_parser('prepare')
    p=sub.add_parser('freeze');p.add_argument('--output',required=True,type=Path)
    p=sub.add_parser('build');p.add_argument('--freeze',required=True,type=Path)
    args=ap.parse_args()
    if args.action=='prepare':prepare()
    elif args.action=='freeze':freeze(args.output)
    else:build(args.freeze)
