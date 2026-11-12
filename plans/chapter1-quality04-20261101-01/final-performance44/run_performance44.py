"""Root-scheduled real-time probe. No GPU action on import; run waits in MENU.

Root must reserve the sole GPU, launch, focus the game with CUA, then click Start.
Never pass autostart, screenshots, movie, fixed FPS, ignore-focus, or wall quit.
"""
from pathlib import Path
import argparse,csv,hashlib,json,math,subprocess,time,shutil,struct,zlib,traceback
ROOT=Path('C:/Project/d2r-combat-baseline')
SCRIPT=Path(__file__).resolve().parent
HERE=SCRIPT
EXE=ROOT/'builds/chapter1/chapter1-full-candidate-20261113-44/AshenCloister-Chapter1.exe'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
    p=Path(p)
    assert not p.exists(),f'Preserve prior evidence: {p}'
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,ensure_ascii=False);f.write('\n')

FULL=SCRIPT.parent/'full44'
BUILD_ID='chapter1-full-candidate-20261113-44'
SESSION_ROOT=SCRIPT/'sessions'
HERE=SESSION_ROOT/'unbound'
PINFILE=HERE/'session-bind.json'
NAMES=['frame_probe_render44.gd','performance44_observer.gd']
RUN_IDS=['run-01','run-02','run-03']
BOUNDARY_US=1000000
MIN_SAMPLES=300

def canonical_session(name):
    assert name and all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in name),'Invalid session ID'
    p=(SESSION_ROOT/name).resolve()
    assert p.parent==SESSION_ROOT.resolve() and p.name==name
    return p

def activate(name):
    global HERE,PINFILE
    HERE=canonical_session(name);PINFILE=HERE/'session-bind.json'

def canonical_run(run_id):
    assert run_id in RUN_IDS,'Use exactly run-01, run-02, run-03; no cherry-picking'
    return HERE/'runs'/run_id

def check_pins(base,pins):
    bad=[p for p,h in pins.items() if not (base/p).is_file() or sha(base/p)!=h]
    assert not bad,{'base':str(base),'mismatches':bad}

def current_profiles():
    import os
    appdata=Path(os.environ['APPDATA'])
    folders=sorted(p for p in appdata.glob('AshenCloisterChapterOneQuality*') if p.is_dir())
    assert (appdata/'AshenCloisterChapterOneQuality44/chapter-one-profile-v1.json').is_file(),'Selected44 profile must already exist from approved package fork'
    pins={}
    for folder in folders:
        paths=([folder/'chapter-one-profile-v1.json'] if (folder/'chapter-one-profile-v1.json').is_file() else [])+sorted(folder.glob('chapter-one-profile-v1.revision-*.json'))
        for p in paths:pins[str(p.resolve())]=sha(p)
    return pins

def package_snapshot():
    # Only the approved44 package is eligible: never silently benchmark41/40/38.
    names=['FINAL-SOURCE-FREEZE.json','staging-manifest.json','build.json','closure.json','pck-audit.json','PACKAGED-INTEGRATION.json','packaged-integration-execution.json','FINAL-PRESERVATION.json']
    docs={n:read(FULL/n) for n in names}
    build=docs['build.json'];closure=docs['closure.json'];execution=docs['packaged-integration-execution.json']
    assert closure['build_id']==BUILD_ID
    assert execution['actual_exit']==0 and execution['timed_out'] is False and execution.get('launch_error','missing') is None
    assert docs['PACKAGED-INTEGRATION.json']['success'] is True and docs['pck-audit.json']['success'] is True and docs['FINAL-PRESERVATION.json']['success'] is True
    paths=closure['runtime_source_files']
    assert len(paths)==183 and len(set(paths))==183 and build['runtime_count']==183,'Reconcile actual44 closure before binding; do not weaken the gate'
    required={'chapter1/view/chapter_actors_quality42.gd','chapter1/view/ui41/chapter_hud_quality41.gd','chapter1/view/ui40/chapter_hud_quality40.gd','chapter1/view/chapter_elements_quality39.gd','chapter1/art/portrait41/oath_witch_portrait_v01.png','chapter1/art/portrait41/ATTRIBUTION.ko.md'}
    required|={'chapter1/view/chapter_elements_quality43.gd'}|{'chapter1/view/ember_'+part+'_quality43.gdshader' for part in ['core','afterglow','contact']}
    required|={'chapter1/view/chapter_elements_quality44.gd'}|{'chapter1/view/arc_'+part+'_quality44.gdshader' for part in ['core','contact']}
    assert required.issubset(paths)
    assert closure['stage_count']==185 and build['stage_count']==185 and len(docs['staging-manifest.json'])==185
    # Root freeze includes the183 runtime files plus its unchanged project/preset.
    assert set(docs['FINAL-SOURCE-FREEZE.json'])==set(paths)|{'project.godot','export_presets.cfg'}
    assert len(docs['FINAL-SOURCE-FREEZE.json'])==185
    stage=Path(closure['stage']).resolve()
    assert stage==Path('C:/Project/game-research/build-staging')/BUILD_ID
    assert Path(build['exe']).resolve()==EXE.resolve() and EXE.is_file() and EXE.stat().st_size==build['bytes'] and sha(EXE)==build['sha256']
    check_pins(ROOT,docs['FINAL-SOURCE-FREEZE.json']);check_pins(stage,docs['staging-manifest.json'])
    manifests={str((FULL/n).resolve()):sha(FULL/n) for n in names}
    previous={}
    # Historical source is proved by its immutable stage and manifests, not by
    # incorrectly demanding that today's root assembly still be version37.
    for proof in [SCRIPT.parent/'full37/build',SCRIPT.parent/'ui38/package38',SCRIPT.parent/'full40',SCRIPT.parent/'full41',SCRIPT.parent/'full42',SCRIPT.parent/'full43']:
        old_closure=read(proof/'closure.json');old_build=read(proof/'build.json');old_stage=Path(old_closure['stage'])
        old_pins=read(proof/'staging-manifest.json');check_pins(old_stage,old_pins)
        assert sha(old_build['exe'])==old_build['sha256']
        freeze=proof.parent/'FINAL-SOURCE-FREEZE.json' if proof.name=='build' else proof/'FINAL-SOURCE-FREEZE.json'
        assert freeze.is_file()
        previous[old_closure['build_id']]={'exe':old_build['exe'],'sha256':old_build['sha256'],'stage':str(old_stage),'stage_pins':old_pins,'manifest_sha256':{str(p.resolve()):sha(p) for p in [proof/'closure.json',proof/'build.json',proof/'staging-manifest.json',freeze]}}
    # Preserve41's original failed export attempt too; successful attempt02
    # does not replace its immutable evidence or executable.
    original41=SCRIPT.parent/'full41/ATTEMPT01-PRESERVED.json'
    first=read(original41);check_pins(Path(first['stage']),first['stage_files'])
    assert sha(first['exe'])==first['exe_sha256']
    previous['candidate41-original-attempt01']={'manifest_sha256':sha(original41),'stage':first['stage'],'stage_pins':first['stage_files'],'exe':first['exe'],'sha256':first['exe_sha256']}
    return {'build_id':BUILD_ID,'exe_sha256':build['sha256'],'manifest_sha256':manifests,'user_pins':current_profiles(),'root_payload_files':len(docs['FINAL-SOURCE-FREEZE.json']),'stage_payload_files':len(docs['staging-manifest.json']),'stage':str(stage),'previous_packages':previous}

def bind(session):
    activate(session)
    assert not HERE.exists(),'Use a fresh session; preserve all previous attempts'
    payload=package_snapshot()
    result=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object {$_.Name -like 'Godot*' -or $_.Name -like 'AshenCloister*'} | Select-Object -ExpandProperty ProcessId"],capture_output=True,text=True,check=True)
    assert not result.stdout.strip(),'A game/engine is already running; do not disturb it'
    write(PINFILE,{'session':session,'preservation':payload,'observer_pins':{n:sha(SCRIPT/n) for n in NAMES},'run_ids':RUN_IDS,'scope':'Frozen44 package and current user profiles before all three real-time runs. Hashes only; no profile writes or restoration.'})
    print(json.dumps({'bound':session,'build_id':BUILD_ID,'exe_sha256':payload['exe_sha256'],'runs':RUN_IDS}))

def preservation(pins_file):
    assert Path(pins_file).resolve()==PINFILE.resolve(),'Use this immutable session binding'
    binding=read(PINFILE)
    assert binding['run_ids']==RUN_IDS and binding['session']==HERE.name
    assert binding['observer_pins']=={n:sha(SCRIPT/n) for n in NAMES},'Observer changed after binding'
    current=package_snapshot()
    assert current==binding['preservation'],'Package/stage/current profiles changed. Preserve and stop; never restore old progress.'
    return {**current,'session_binding_sha256':sha(PINFILE)}


def command_for(probe):
    return [str(EXE),'--script',str(SCRIPT/'performance44_observer.gd'),'--windowed','--resolution','1920x1080','--rendering-method','forward_plus','--disable-vsync','--max-fps','0','--delta-smoothing','disable','--','--chapter1-profile-off','--chapter1-pilot','--chapter1-seed=90131','--chapter1-primary=chapter1.skill.frost','--performance44-dir='+str(probe)]

def own_process(command,folder,label,timeout):
    process=None;timed_out=False;exception=None;exit_code=None;started=time.monotonic()
    try:
        with (folder/(label+'.stdout.txt')).open('xb') as out,(folder/(label+'.stderr.txt')).open('xb') as err:
            process=subprocess.Popen(command,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
            write(folder/(label+'-process.json'),{'pid':process.pid,'command':command,'owned_by_this_runner':True})
            print(json.dumps({'phase':label,'pid':process.pid,'focus_menu_then_click_start':label=='native'}),flush=True)
            try:exit_code=process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:timed_out=True;raise
    except Exception as exc:exception=type(exc).__name__+': '+str(exc)
    finally:
        if process is not None:
            if process.poll() is None:
                try:process.terminate();process.wait(timeout=5)
                except Exception:
                    if process.poll() is None:
                        process.kill()
                        try:process.wait(timeout=5)
                        except Exception as exc:exception=(exception or '')+'; final reap: '+str(exc)
            exit_code=process.poll()
        result={'actual_exit':exit_code,'timeout':timed_out,'exception':exception,'wall_seconds':time.monotonic()-started}
        write(folder/(label+'-execution.json'),result)
    return result

def run(run_id,pins_file):
    folder=canonical_run(run_id);assert not folder.exists(),'Choose a fresh run ID'
    folder.mkdir(parents=True);failure=None;before=None;native=None
    probe=EXE.parent/'qa-probe'/('quality44-'+HERE.name+'-'+run_id)
    try:
        assert not probe.exists(),'Choose a fresh runtime probe directory'
        before=preservation(pins_file);write(folder/'preservation-before.json',before)
        observer_pins={n:sha(SCRIPT/n) for n in NAMES}
        launch={'command':command_for(probe),'exe_sha256':before['exe_sha256'],'observer_pins':observer_pins,'runtime_directory':str(probe.resolve()),'autostart':False,'scope':'Candidate44 first70seconds representative normalpilot; root nativeMENUfocus/start; exclusive CPU/GPU required; not fullchapter worstcase'}
        write(folder/'launch.json',launch)
        for n in NAMES:shutil.copy2(SCRIPT/n,folder/n)
        for n in NAMES:
            checked=own_process([str(EXE),'--headless','--check-only','--script',str(SCRIPT/n)],folder,n+'.check',45)
            assert checked['actual_exit']==0 and not checked['timeout'] and not checked['exception'] and (folder/(n+'.check.stderr.txt')).stat().st_size==0,'Check-only failed'
        native=own_process(launch['command'],folder,'native',300)
    except Exception as exc:failure=type(exc).__name__+': '+str(exc)
    finally:
        execution=dict(native or {'actual_exit':None,'timeout':False,'exception':failure})
        execution.update({'runner_exception':failure,'exe_sha256_after':sha(EXE) if EXE.is_file() else None,'observer_pins_after':{n:sha(SCRIPT/n) for n in NAMES}})
        execution['exe_unchanged']=before is not None and execution['exe_sha256_after']==before['exe_sha256']
        write(folder/'execution.json',execution)
        try:
            if (probe/'probe').is_dir():shutil.copytree(probe/'probe',folder/'probe')
            for n in ['preflight.png','postflight.png','postflight.json']:
                if (probe/n).is_file():shutil.copy2(probe/n,folder/n)
            if (probe/'probe').is_dir():write(folder/'probe-copy.json',{'runtime_directory':str(probe.resolve()),'files':{p.name:sha(p) for p in (probe/'probe').iterdir() if p.is_file()},'copied_sha256':{p.name:sha(p) for p in (folder/'probe').iterdir() if p.is_file()}})
        except Exception as exc:write(folder/'artifact-copy-failure.json',{'exception':str(exc)})
        try:write(folder/'preservation-after.json',preservation(pins_file))
        except Exception as exc:write(folder/'preservation-after-failure.json',{'exception':str(exc)})
        result=audit(folder)
    return result

def _compute_audit(folder):
    folder=Path(folder).resolve()
    assert folder.is_relative_to(HERE/'runs')
    errors=[]
    probe=folder/'probe'
    if not all((probe/p).is_file() for p in ('metadata.json','frames.csv','summary.json','final-context.json')) or not (folder/'postflight.json').is_file():
        errors.append('incomplete_probe_artifacts')
        result={'valid':False,'errors':errors,'scope':'Independent raw audit; no invented missing samples'}
        return result
    meta=read(probe/'metadata.json');summary=read(probe/'summary.json')
    post=read(folder/'postflight.json');assert post['fx_script']=='res://chapter1/view/chapter_elements_quality44.gd' and post['hud_script']=='res://chapter1/view/ui41/chapter_hud_quality41.gd' and post['actor_script']=='res://chapter1/view/chapter_actors_quality42.gd' and post['world_script']=='res://chapter1/view/chapter_world_quality37c.gd' and post['core_script']=='res://chapter1/core/chapter_run_quality37.gd';final=read(probe/'final-context.json')
    if meta['actual_readback_before']!=[1920,1080] or post['actual_after']!=[1920,1080]:errors.append('actual_readback_not_1080p')
    if final.get('render_invariant_errors',None)!=[]:errors.append('render_invariants_not_constant')
    if final.get('actual_scenario_at_start')!={'seed':90131,'primary':'chapter1.skill.frost'} or final.get('actual_scenario_at_end')!={'seed':90131,'primary':'chapter1.skill.frost'} or final.get('actual_core_primary_at_start')!='chapter1.skill.frost' or final.get('actual_core_primary_at_end')!='chapter1.skill.frost' or final.get('scenario_errors',None)!=[]:errors.append('actual_seed_or_primary_not_fixed')
    if meta['render_invariant']['scale3d']!=1.0 or meta['render_invariant']['msaa']!=2:errors.append('render_scale_or_msaa_changed')
    for image_name in ['preflight.png','postflight.png']:
        png=(folder/image_name).read_bytes()
        if len(png)<33 or png[:8]!=b'\x89PNG\r\n\x1a\n' or png[8:16]!=b'\x00\x00\x00\x0dIHDR' or zlib.crc32(png[12:29])!=struct.unpack('>I',png[29:33])[0] or struct.unpack('>II',png[16:24])!=(1920,1080):errors.append('invalid_png_or_non1080p')
    with (probe/'frames.csv').open(newline='',encoding='utf-8') as f:rows=[{k:int(v) for k,v in r.items()} for r in csv.DictReader(f)]
    intervals=[];prior=None
    for i,row in enumerate(rows):
        if row['sequence']!=i:errors.append('sequence_gap')
        if prior is not None and row['interval_us']!=row['elapsed_us']-prior['elapsed_us']:errors.append('raw_interval_mismatch')
        if prior is not None and row['process_frame']!=prior['process_frame']+1:errors.append('missing_process_callback')
        if prior is not None and (row['frames_drawn']<prior['frames_drawn'] or row['physics_frame']<prior['physics_frame'] or row['sim_tick']<prior['sim_tick']):errors.append('counter_regression')
        expected_phase=0 if prior is None or row['elapsed_us']<10000000 else (1 if prior['elapsed_us']>=10000000 else 3)
        if row['phase']!=expected_phase:errors.append('phase_mismatch')
        if not row['focused']:errors.append('unfocused_armed_frame')
        if row['mode_code'] not in (1,2):errors.append('terminal_or_nonplaying_armed_frame')
        if tuple(row[k] for k in ('window_width','window_height','texture_reported_width','texture_reported_height'))!=(1920,1080,*meta['reported_texture_size']):errors.append('wrong_window_or_reported_texture_size')
        if row['phase']==1:intervals.append(row['interval_us'])
        prior=row
    if len(intervals)<MIN_SAMPLES:errors.append('insufficient_measured_callbacks_retained_raw')
    if rows and rows[0]['phase']!=0:errors.append('invalid_initial_phase')
    if any(r['interval_us']<=0 for r in rows[1:]):errors.append('nonpositive_interval_any_phase')
    if any(rows[i]['elapsed_us']<=rows[i-1]['elapsed_us'] for i in range(1,len(rows))):errors.append('elapsed_not_strictly_increasing')
    boundary=[r for r in rows if r['phase']==3]
    measured=[r for r in rows if r['phase']==1]
    if len(boundary)!=1:errors.append('warmup_crossing_count')
    first=measured[0]['elapsed_us']-measured[0]['interval_us'] if measured else -1
    last=measured[-1]['elapsed_us'] if measured else -1
    if not 10000000<=first<=10000000+BOUNDARY_US:errors.append('warmup_boundary_stall_over1s_raw_retained')
    if not 70000000<=last<=70000000+BOUNDARY_US:errors.append('sample_end_stall_over1s_raw_retained')
    if len(rows)<2 or rows[-2]['elapsed_us']>=70000000:errors.append('not_first70s_crossing')
    if rows and sum(r['interval_us'] for r in rows)!=rows[-1]['elapsed_us']:errors.append('whole_raw_sum_not_telescoping')
    if measured and sum(intervals)!=last-first:errors.append('measured_sum_not_telescoping')
    if summary.get('first_interval_start_us')!=first or summary.get('last_interval_end_us')!=last:errors.append('summary_boundary_fields_mismatch')
    if len(rows)>180000 or summary['overflow']:errors.append('capacity_invalid')
    if not rows or rows[0]['elapsed_us']!=0 or rows[0]['interval_us']!=0:errors.append('invalid_first_callback')
    if not rows or rows[-1]['elapsed_us']<70000000:errors.append('sample_end_not_reached')
    if rows and (rows[-1]['frames_drawn']<=rows[0]['frames_drawn'] or rows[-1]['sim_tick']<=rows[0]['sim_tick']):errors.append('render_or_simulation_not_progressing')
    if sum(intervals)<59000000 or any(v<=0 for v in intervals):errors.append('invalid_sample_duration_or_interval')
    if not summary['eligible_representative_run']:errors.extend(summary['eligibility_errors'])
    if not meta.get('profile_disabled',False) or not meta.get('pilot',False) or meta.get('qa_ignore_focus',True):errors.append('wrong_profile_or_input_policy')
    if meta.get('time_scale')!=1.0:errors.append('time_scale_not_one')
    if any(v in meta.get('user_args',[]) for v in ['--chapter1-start','--chapter1-qa-ignore-focus']):errors.append('forbidden_autostart_or_ignore_focus')
    if meta.get('delta_smoothing',True):errors.append('delta_smoothing_enabled')
    if meta['max_fps']!=0 or meta['vsync_mode']!=0 or meta['display_server']=='headless' or meta['rendering_method']!='forward_plus':errors.append('invalid_engine_configuration')
    if summary['raw_csv_sha256']!=sha(probe/'frames.csv'):errors.append('raw_sha_mismatch')
    if summary['measured_samples']!=len(intervals) or summary['rows']!=len(rows) or summary['measured_interval_sum_us']!=sum(intervals):errors.append('summary_counts_mismatch')
    ordered=sorted(intervals)
    def quantile(p):return ordered[max(0,math.ceil(len(ordered)*p)-1)]/1000 if ordered else None
    for key,p in (('p50_ms',.5),('p95_ms',.95),('p99_ms',.99)):
        if quantile(p)!=summary[key]:errors.append('summary_quantile_mismatch_'+key)
    if summary.get('worst_ms')!=(max(intervals)/1000 if intervals else 0):errors.append('summary_worst_mismatch')
    recomputed_target=not errors and quantile(.95) is not None and quantile(.95)<=16.67
    if summary.get('target_met_for_this_run')!=recomputed_target:errors.append('summary_target_flag_mismatch')
    launch=read(folder/'launch.json');execution=read(folder/'execution.json')
    runtime=Path(launch['runtime_directory']).resolve()
    expected_runtime=(EXE.parent/'qa-probe'/('quality44-'+HERE.name+'-'+folder.name)).resolve()
    if runtime!=expected_runtime or launch['command']!=command_for(expected_runtime):errors.append('launch_command_or_runtime_mismatch')
    if launch['autostart'] is not False:errors.append('launch_autostart')
    for n,h in launch['observer_pins'].items():
        if n not in NAMES or sha(folder/n)!=h or sha(SCRIPT/n)!=h or execution['observer_pins_after'].get(n)!=h:errors.append('observer_source_hash_changed')
    if set(launch['observer_pins'])!=set(NAMES):errors.append('wrong_observer_set')
    copy=read(folder/'probe-copy.json')
    if Path(copy['runtime_directory']).resolve()!=runtime:errors.append('copy_runtime_identity_mismatch')
    for n in ['metadata.json','frames.csv','summary.json','final-context.json']:
        if sha(runtime/'probe'/n)!=sha(probe/n) or copy['files'].get(n)!=sha(probe/n) or copy['copied_sha256'].get(n)!=sha(probe/n):errors.append('runtime_raw_copy_hash_mismatch')
    for n in ['preflight.png','postflight.png','postflight.json']:
        if sha(runtime/n)!=sha(folder/n):errors.append('runtime_postflight_copy_hash_mismatch')
    if str(meta['render_invariant']['window'])!='(1920, 1080)' or str(post['window_after'])!='(1920, 1080)':errors.append('before_after_window_not1080')
    if any(meta.get(k) for k in ['movie_path','captures_enabled','input_log_enabled','wall_quit_enabled']):errors.append('forbidden_metadata_io_or_movie')
    if any(v in meta.get('engine_args',[]) for v in ['--fixed-fps','--disable-render-loop','--write-movie']):errors.append('forbidden_engine_mode')
    if '--chapter1-profile-off' not in meta.get('user_args',[]):errors.append('profileoff_arg_absent')
    if any(v.startswith(('--chapter1-capture-dir','--chapter1-qa-input-log','--chapter1-quit-after')) for v in meta.get('user_args',[])):errors.append('forbidden_qa_io_args')
    if execution.get('runner_exception') or execution.get('exception'):errors.append('runner_or_process_exception')
    if execution['actual_exit']!=0 or execution['timeout'] or not execution['exe_unchanged']:errors.append('execution_failed_or_changed')
    logs=(folder/'native.stdout.txt').read_text(encoding='utf-8')+(folder/'native.stderr.txt').read_text(encoding='utf-8')
    if any(s in logs for s in ('SCRIPT ERROR','ERROR:','WARNING:')):errors.append('engine_error_or_warning')
    if not all((folder/p).is_file() for p in ['preservation-before.json','preservation-after.json']):errors.append('missing_preservation_proof')
    elif read(folder/'preservation-before.json')!=read(folder/'preservation-after.json'):errors.append('payload_or_user_pins_changed')
    if read(folder/'preservation-before.json')!=preservation(PINFILE):errors.append('current_bound_package_or_pins_changed')
    result={'valid':not errors,'target_met_for_this_run':not errors and quantile(.95) is not None and quantile(.95)<=16.67,'errors':sorted(set(errors)),'raw_sha256':sha(probe/'frames.csv'),'raw_rows':len(rows),
            'measured_intervals':len(intervals),'measured_interval_sum_us':sum(intervals),'p50_ms':quantile(.5),'p95_ms':quantile(.95),
            'p99_ms':quantile(.99),'worst_ms':max(intervals)/1000 if intervals else None,'actual_readback':[meta['actual_readback_before'],post['actual_after']],'reported_texture':meta['reported_texture_size'],'scope':'Candidate44 first70seconds representative normal policy, not fullchapter maximum load. Independent raw monotonic callback intervals. Live readback1080p before/after, per-frame render invariants; reported texture size retained separately. Not hardware GPU time or fixed60FPS.'}
    return result

def evidence_hashes(folder):
    folder=Path(folder).resolve();files={str(p.relative_to(folder)):sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='independent-audit.json'}
    return files

def compute_audit(folder):
    folder=Path(folder).resolve()
    try:
        assert canonical_run(folder.name)==folder
        result=_compute_audit(folder)
    except Exception as exc:result={'valid':False,'errors':['audit_exception:'+type(exc).__name__+':'+str(exc)],'scope':'Missing or inconsistent raw artifacts are invalid; no fabricated samples'}
    result['evidence_sha256']=evidence_hashes(folder)
    return result

def audit(folder):
    result=compute_audit(folder)
    write(Path(folder)/'independent-audit.json',result);print(json.dumps(result));return result

def aggregate(run_ids,output):
    assert run_ids==RUN_IDS,'Use the fixed three runs from this bound session, without cherry-picking'
    assert Path(output).name==output and output.endswith('.json'),'Fresh summary JSON filename required'
    runs=[canonical_run(s) for s in run_ids]
    assert len(set(runs))==3
    audits=[compute_audit(r) for r in runs]
    saved=[read(r/'independent-audit.json') if (r/'independent-audit.json').is_file() else None for r in runs]
    unchanged=all(a==b for a,b in zip(audits,saved))
    launches=[read(r/'launch.json') if (r/'launch.json').is_file() else None for r in runs]
    preserved=[read(r/'preservation-after.json') if (r/'preservation-after.json').is_file() else None for r in runs]
    if any(v is None for v in launches+preserved):
        result={'runs':run_ids,'eligible_three_runs':False,'target_met_all_three':False,'errors':['missing_launch_or_preservation'],'fresh_audits':audits,'scope':'Missing evidence is invalid; no invented measurements'}
        write(HERE/output,result)
        return result
    same_observers=all(v['observer_pins']==launches[0]['observer_pins'] for v in launches)
    same_payload=all(v==preserved[0] for v in preserved)
    runtimes=[Path(v['runtime_directory']).resolve() for v in launches]
    unique_raw=len(set(runtimes))==3
    eligible=unchanged and unique_raw and all(a['valid'] for a in audits) and len({v['exe_sha256'] for v in launches})==1 and same_observers and same_payload
    result={'runs':run_ids,'same_exe':len({v['exe_sha256'] for v in launches})==1,
          'fresh_reaudit_matches_saved':unchanged,'three_distinct_runtime_identities':unique_raw,'same_observers':same_observers,'same_frozen_payload_and_user_pins':same_payload,'eligible_three_runs':eligible,'target_p95_ms':16.67,'target_met_all_three':eligible and all(a['p95_ms']<=16.67 for a in audits),
          'audits':audits,'scope':'Exactly3 unique first70seconds representative normal-pilot runs on frozen candidate44; not fullchapter worstcase,synthetic maximumload,allframes60FPS,or hardwareGPU timer'}
    write(HERE/output,result)
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='action',required=True)
    p=sub.add_parser('bind');p.add_argument('--session',required=True)
    p=sub.add_parser('run');p.add_argument('--session',required=True);p.add_argument('--run-id',required=True)
    p=sub.add_parser('audit');p.add_argument('--session',required=True);p.add_argument('--run-id',required=True)
    p=sub.add_parser('aggregate');p.add_argument('--session',required=True);p.add_argument('--output',required=True)
    args=ap.parse_args()
    if args.action=='bind':bind(args.session)
    else:
        activate(args.session)
        if args.action=='run':result=run(args.run_id,PINFILE)
        elif args.action=='audit':result=audit(canonical_run(args.run_id))
        else:result=aggregate(RUN_IDS,args.output)
        raise SystemExit(0 if result.get('target_met_for_this_run',result.get('target_met_all_three',False)) else 1)
