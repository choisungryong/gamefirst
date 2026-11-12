"""Read-only, bounded source catalog. No Godot execution or arbitrary evaluation."""
from pathlib import Path
import collections, datetime, hashlib, json, re, struct
ROOT = Path(__file__).resolve().parents[2]
PLAN = 'plans/chapter1-presentation-roadmap-20261107-01'
BOOK = 'plans/chapter1-quality04-20261101-01/full30/book-v44/dist'
CLOSURE = 'plans/chapter1-quality04-20261101-01/full37/build/closure.json'
CANDIDATE38 = 'plans/chapter1-quality04-20261101-01/ui38/package38'
PORTRAIT_DIR = 'chapter1/art/portrait41'
PORTRAIT_PNG = PORTRAIT_DIR+'/oath_witch_portrait_v01.png'
UI38_FILES = {'chapter1/view/ui38/chapter_hud_quality38.gd','chapter1/view/ui38/element_seal.gd','chapter1/view/ui38/life_seal.gd'}
FX39_FILES = {'chapter1/view/chapter_elements_quality39.gd'}|{'chapter1/view/frost_'+part+'_quality39.gdshader' for part in ['core','contact','fracture','release']}
UI40_FILE = 'chapter1/view/ui40/chapter_hud_quality40.gd'
CANDIDATE40 = 'plans/chapter1-quality04-20261101-01/full40'
CANDIDATE41 = 'plans/chapter1-quality04-20261101-01/full41'
CANDIDATE42 = 'plans/chapter1-quality04-20261101-01/full42'
CANDIDATE43 = 'plans/chapter1-quality04-20261101-01/full43'
FIRE43_FILES = {'chapter1/view/chapter_elements_quality43.gd'}|{'chapter1/view/ember_'+part+'_quality43.gdshader' for part in ['core','afterglow','contact']}
CANDIDATE44 = 'plans/chapter1-quality04-20261101-01/full44'
ARC44_FILES = {'chapter1/view/chapter_elements_quality44.gd'}|{'chapter1/view/arc_'+part+'_quality44.gdshader' for part in ['core','contact']}
UI41_FILE = 'chapter1/view/ui41/chapter_hud_quality41.gd'
PORTRAIT_ATTRIBUTION = PORTRAIT_DIR+'/ATTRIBUTION.ko.md'
CANDIDATES = (
    {'explicit_launch_error':True,'number':44,'directory':CANDIDATE44,'build_id':'chapter1-full-candidate-20261113-44','count':183,'required':UI38_FILES|FX39_FILES|FIRE43_FILES|ARC44_FILES|{UI40_FILE,UI41_FILE,PORTRAIT_PNG,PORTRAIT_ATTRIBUTION,'chapter1/view/chapter_actors_quality42.gd'},'preservation_fields':['success','preserved_previous_builds','source44_and_stage44_unchanged','profiles_byte_identical']},
    {'explicit_launch_error':True,'number':43,'directory':CANDIDATE43,'build_id':'chapter1-full-candidate-20261113-43','count':180,'required':UI38_FILES|FX39_FILES|FIRE43_FILES|{UI40_FILE,UI41_FILE,PORTRAIT_PNG,PORTRAIT_ATTRIBUTION,'chapter1/view/chapter_actors_quality42.gd'},'preservation_fields':['success','preserved_previous_builds','source43_and_stage43_unchanged','profiles_byte_identical']},
    {'explicit_launch_error':True,'number':42,'directory':CANDIDATE42,'build_id':'chapter1-full-candidate-20261113-42','count':176,'required':UI38_FILES|FX39_FILES|{UI40_FILE,UI41_FILE,PORTRAIT_PNG,PORTRAIT_ATTRIBUTION,'chapter1/view/chapter_actors_quality42.gd'},'preservation_fields':['success','preserved_previous_builds','source42_and_stage42_unchanged','profiles_byte_identical']},
    {'explicit_launch_error':True,'number':41,'directory':CANDIDATE41,'build_id':'chapter1-full-candidate-20261112-41','count':175,'required':UI38_FILES|FX39_FILES|{UI40_FILE,UI41_FILE,PORTRAIT_PNG,PORTRAIT_ATTRIBUTION},'preservation_fields':['success','preserved_previous_builds','source41_and_stage41_unchanged','profiles_byte_identical']},
    {'explicit_launch_error':True,'number':40,'directory':CANDIDATE40,'build_id':'chapter1-full-candidate-20261111-40','count':172,'required':UI38_FILES|FX39_FILES|{UI40_FILE}},
    {'explicit_launch_error':False,'number':38,'directory':CANDIDATE38,'build_id':'chapter1-full-candidate-20261107-38','count':166,'required':UI38_FILES},
)

def read(path):
    return (ROOT/path).read_text(encoding='utf-8-sig')

def verified_candidate(directory, root=ROOT, specification=None):
    """Select only a complete successful package, never a partially written build."""
    try:
        spec=specification or next((s for s in CANDIDATES if s['directory']==directory),CANDIDATES[-1])
        count=spec['count'];required=spec['required']
        folder=root/directory
        closure=json.loads((folder/'closure.json').read_text(encoding='utf-8-sig'))
        build=json.loads((folder/'build.json').read_text(encoding='utf-8-sig'))
        execution=json.loads((folder/'packaged-integration-execution.json').read_text(encoding='utf-8-sig'))
        integration=json.loads((folder/'PACKAGED-INTEGRATION.json').read_text(encoding='utf-8-sig'))
        audit=json.loads((folder/'pck-audit.json').read_text(encoding='utf-8-sig'))
        if spec.get('preservation_fields'):
            preservation=json.loads((folder/'FINAL-PRESERVATION.json').read_text(encoding='utf-8-sig'))
            if any(preservation.get(key) is not True for key in spec['preservation_fields']): return None
        paths=closure['runtime_source_files']; exe=Path(build['exe'])
        if execution.get('actual_exit')!=0 or execution.get('timed_out') is not False or (spec['explicit_launch_error'] and 'launch_error' not in execution) or execution.get('launch_error') is not None or integration.get('success') is not True or audit.get('success') is not True: return None
        if len(paths)!=count or len(set(paths))!=count or not required.issubset(paths) or build.get('runtime_count',build.get('source_count'))!=count: return None
        if closure.get('build_id')!=spec['build_id']: return None
        if any(not isinstance(p,str) or Path(p).is_absolute() or '..' in Path(p).parts or ':' in p or not (root/p).resolve().is_relative_to(root.resolve()) for p in paths): return None
        if any(not (root/p).is_file() for p in paths): return None
        if not exe.resolve().is_relative_to((root/'builds/chapter1').resolve()) or not exe.is_file() or exe.stat().st_size!=build['bytes']: return None
        if hashlib.sha256(exe.read_bytes()).hexdigest()!=build['sha256']: return None
        return closure,build
    except (OSError,ValueError,KeyError,TypeError):
        return None

def selected_build():
    for specification in CANDIDATES:
        selected=verified_candidate(specification['directory'],specification=specification)
        if selected: return specification['directory']+'/closure.json',selected[0],selected[1]
    return CLOSURE,json.loads(read(CLOSURE)),json.loads(read(str(Path(CLOSURE).parent/'build.json')))

def literal(text, name, vectors=False):
    match = re.search(r'const\s+'+re.escape(name)+r'\s*(?::=|=)\s*', text)
    if not match: raise ValueError('Missing constant '+name)
    start=match.end(); opener=text[start]; closer={'[':']','{':'}'}[opener]
    depth=0; quoted=False; escape=False
    for i in range(start,len(text)):
        c=text[i]
        if quoted:
            if escape: escape=False
            elif c=='\\': escape=True
            elif c=='"': quoted=False
        elif c=='"': quoted=True
        elif c==opener: depth+=1
        elif c==closer:
            depth-=1
            if depth==0:
                raw=text[start:i+1]
                if vectors: raw=re.sub(r'Vector2\(\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)',r'[\1,\2]',raw)
                return json.loads(raw),text[:start].count('\n')+1
    raise ValueError('Unclosed '+name)

def glb_metadata(path):
    with path.open('rb') as f:
        magic,version,length=struct.unpack('<4sII',f.read(12))
        if magic!=b'glTF' or version!=2: raise ValueError('Not GLB2')
        size,kind=struct.unpack('<II',f.read(8))
        if kind!=0x4e4f534a or size>32*1024*1024: raise ValueError('Invalid JSON chunk')
        doc=json.loads(f.read(size))
    nodes=doc.get('nodes',[])
    return {'meshes':[m.get('name',str(i)) for i,m in enumerate(doc.get('meshes',[]))], 'skins':[{'name':s.get('name',''),'joints':len(s.get('joints',[])),'bones':[nodes[n].get('name',str(n)) for n in s.get('joints',[])]} for s in doc.get('skins',[])], 'animations':[{'name':a.get('name',str(i)), 'channels':len(a.get('channels',[]))} for i,a in enumerate(doc.get('animations',[]))], 'nodes':len(nodes), 'preview_note':'GLB 원본입니다. 애니메이션 재생에는 호환 뷰어가 필요합니다.'}

def generate():
    warnings=[]; entities=[]; files=[]
    closure_path,closure,build_info=selected_build(); packaged=set(closure['runtime_source_files'])
    candidate_sources=UI38_FILES|FX39_FILES|{UI40_FILE,UI41_FILE}
    source_paths=packaged|{p for p in candidate_sources if (ROOT/p).is_file()}
    refs={}; texts={}
    for p in sorted(source_paths):
        if Path(p).suffix in ('.gd','.tscn','.gdshader','.json'):
            try: texts[p]=read(p)
            except (OSError,UnicodeError) as e: warnings.append(str(e))
    for p,t in texts.items():
        refs[p]=sorted(set(re.findall(r'res://([^"\s\)]+)',t)))
    # Runtime scene edges identify actual inheritance, not filename age.
    entry=closure.get('entry_scene','chapter1/ChapterOne.tscn')
    entry_scripts=set(refs.get(entry,[]))
    # Direct means selected entry / controller declarations, inherited means transitive dependencies.
    direct={entry}|entry_scripts
    pending=list(entry_scripts);controller_chain=set()
    while pending:
        p=pending.pop()
        if p in controller_chain or p not in packaged: continue
        controller_chain.add(p);direct.update(refs.get(p,[]))
        pending.extend(re.findall(r'^extends \"res://([^\"]+)\"',texts.get(p,''),re.M))
    active=set(); queue=[entry]
    while queue:
        p=queue.pop()
        if p in active or p not in packaged: continue
        active.add(p);queue.extend(refs.get(p,[]))
    def usage(p):
        if p in active:
            return 'active-direct' if p in direct else 'active-inherited'
        if p.startswith(PORTRAIT_DIR+'/'): return 'packaged-unproven' if p in packaged else 'plan'
        return 'packaged-unproven' if p in packaged else ('plan' if p.startswith(PLAN) or p in candidate_sources else 'legacy-preserved')
    def entity(id,name,category,typ,path,line,attributes,assets=None,task_ids=None):
        row={'id':id,'name':name,'category':category,'type':typ,'usage':usage(path),'source':{'path':path,'line':line},'attributes':attributes,'dependencies':refs.get(path,[]),'assets':assets or [],'provenance':{'kind':'source-derived','note':'원본 정의 또는 구현 근거이며 품질 검수 완료를 뜻하지 않습니다.'},'evidence':[{'path':path,'line':line,'note':'원본 정의'}],'task_ids':task_ids or []}
        entities.append(row);return row
    path='chapter1/core/chapter_items.gd';t=read(path)
    for const,category in [('BASES','equipment'),('AFFIXES','affixes'),('UNIQUES','uniques'),('LIMITS','equipment')]:
        values,line=literal(t,const)
        if isinstance(values,dict): values=[{'id':k,'name':k,'bounds':v} for k,v in values.items()]
        for value in values: entity(category+':'+('limit:' if const=='LIMITS' else '')+value['id'],value.get('name',value['id']),('balance' if const=='LIMITS' else category),const.lower(),path,line,value,task_ids=['U04','L03'])
    path='chapter1/data/growth_quality37.json';doc=json.loads(read(path))
    for category in ['skills','passives']:
        for value in doc[category]:
            line=read(path)[:read(path).find('"'+value['id']+'"')].count('\n')+1
            entity(category+':'+value['id'],value['name'],category,category[:-1],path,line,value,task_ids=['U03','V01'])
    entity('growth:xp','성장 XP 경계','balance','progression',path,1,{'catalog_xp_thresholds':doc['xp_thresholds'],'max_active_skills':doc['max_active_skills'],'max_passives':doc['max_passives']})
    path='chapter1/core/chapter_run.gd';t=read(path)
    positions,line=literal(t,'ZONES',True);names,_=literal(t,'ZONE_NAMES');kills,_=literal(t,'SEAL_KILLS');xp,_=literal(t,'FULL_XP')
    for i,name in enumerate(names): entity('maps:zone:'+str(i),name,'maps','zone',path,line,{'index':i,'position':positions[i],'seal_kills':kills[i]},task_ids=['U06'])
    entities[-4]['attributes']['chapter_xp_thresholds']=xp
    rituals,line=literal(t,'RITUALS',True)
    for value in rituals: entity('rituals:'+value['id'],value['name'],'rituals','ritual',path,line,value)
    path='chapter1/presentation/combat_audio.gd';counts,line=literal(read(path),'COUNTS');cooldowns,_=literal(read(path),'COOLDOWNS')
    audio_names={'fire':'화염 발사','cold':'냉기 발사','lightning':'번개 발사','impact':'명중','death':'적 사망','explosion':'폭발','hurt':'플레이어 피격','drop':'아이템 드롭','pickup':'아이템 회수','equip':'장비 장착','step':'발걸음'}
    for cue,count in counts.items():
        for i in range(count): entity('audio:'+cue+':'+str(i),audio_names[cue]+' '+str(i+1),'audio','cue_variant',path,line,{'cue':cue,'variant':i,'cooldown_ticks':cooldowns[cue]},['chapter1/art/quality03_audio/'+cue+'_'+str(i)+'.wav'],['S01','S02','S03'])
    entity('audio:ambience','환경 앰비언스','audio','loop',path,33,{'loop':True},['chapter1/art/quality03_audio/ambience.wav'],['S06'])
    # Actor role definitions preserve original atlas provenance; runtime presenter graph is separate.
    for p in sorted((ROOT/'chapter1/art/actors').glob('*.json')):
        rel=p.relative_to(ROOT).as_posix(); value=json.loads(read(rel));kind=value.get('kind',p.stem)
        role_names={'hero':'주인공 마녀','walker':'근접 보행 적','ranged':'원거리 적','charger':'돌진 적','elite':'정예 적'}
        entity('actors:'+p.stem,role_names.get(kind,kind),'characters' if kind=='hero' else 'enemies','actor_role',rel,1,value,[s[6:] for s in re.findall(r'res://[^"\s]+',read(rel))],['C03','C05'])
    # Actual role identity stays one record; preserved atlas previews and current model source are distinct.
    for row in [e for e in entities if e['type']=='actor_role']:
        kind=row['attributes'].get('kind',row['id'].split(':')[-1])
        presenter,model,line=(
            ('chapter1/view/rigged_hero_actors.gd','chapter1/art/rigged_mage/v01/mage_animated.glb',4) if kind=='hero' else
            ('chapter1/view/chapter_actors_quality34b.gd','chapter1/art/skeleton_outlaw/v02/skeleton_outlaw_merged.glb',55) if kind=='walker' else
            ('chapter1/view/chapter_actors_quality21.gd','chapter1/art/chained_warden/v01/chained_demon_animated.glb',5) if kind in ['ranged','charger'] else
            ('chapter1/view/chapter_actors_demon19.gd','chapter1/art/chained_warden/v01/chained_demon_animated.glb',8))
        row['attributes']['preserved_atlas_source']=row['source']
        row['attributes']['runtime_presenter']=presenter
        row['attributes']['runtime_role']=kind
        row['attributes']['preview_note']='아틀라스는 보존된 2D 역할 자료이며 GLB는 현재 역할 구현에서 연결된 모델 원본입니다. 외형 변형·역할 조건은 구현 근거를 확인하세요.'
        row['source']={'path':presenter,'line':line}
        row['usage']=usage(presenter)
        row['assets']=[model]+row['assets']
        row['dependencies']=sorted(set(row['dependencies']+[presenter]))
        row['evidence'].append({'path':presenter,'line':line,'note':'역할별 모델 연결 조건'})
    path='chapter1/view/chapter_actors_quality12.gd'
    entity('bosses:warden','회랑의 파수왕','bosses','zone_2_elite_presenter',path,5,{'condition':'kind == elite and zone == 2','runtime_quality_approval':False},['chapter1/art/chained_warden/v01/chained_demon_animated.glb'],['C04','V06'])
    for p,t in sorted(texts.items()):
        if p.endswith('.gd') and ('actors' in p or 'hero' in p):
            entity('actor-class:'+p,'배우 구현 · '+Path(p).stem,'implementation','presenter_class',p,1,{'extends':re.findall(r'^extends\s+(.+)',t,re.M),'role_conditions':re.findall(r'^.*(?:kind[!= ]|kind not in|kind in).+$',t,re.M)[:16],'functions':re.findall(r'^func\s+(\w+)',t,re.M)},[r for r in refs.get(p,[]) if r.endswith(('.glb','.png','.json'))],['C03','C05'])
        category='ui' if 'hud' in p or 'input' in p else ('effects' if any(x in p for x in ['effect','element','shader']) else None)
        if category: entity('implementation:'+p,('UI 구현 · ' if category=='ui' else '효과 구현 · ')+Path(p).stem,'implementation','implementation',p,1,{'extends':re.findall(r'^extends\s+(.+)',t,re.M),'functions':re.findall(r'^func\s+(\w+)',t,re.M)},[r for r in refs.get(p,[]) if Path(r).suffix in ('.png','.svg','.glb','.wav')],['U01'] if category=='ui' else ['V01'])
    # Semantic UI surfaces are one record per actual source function/state, not per versioned class.
    ui_surfaces = [
        ('hud','전투 HUD','chapter1/view/cloister_hud.gd','setup',['U01','U02']),
        ('growth','성장 선택 카드','chapter1/view/cloister_hud.gd','_build_modal',['U03']),
        ('inventory','장비 비교와 장착','chapter1/view/cloister_hud.gd','_inventory',['U04']),
        ('stash','장비 보관함','chapter1/view/chapter_hud.gd','_build_stash',['U05']),
        ('objective','현재 목표와 의식 안내','chapter1/view/chapter_hud.gd','sync',['U06']),
        ('discovery','희귀 장비 발견 표시','chapter1/view/chapter_hud_quality20.gd','_present_discovery20',['L02'])]
    if UI40_FILE in packaged:
        ui_surfaces.append(('result','승리·패배 결과',UI40_FILE,'_build_result40',['U08']))
    if UI41_FILE in packaged:
        ui_surfaces.append(('title','초상 타이틀 메뉴',UI41_FILE,'_build_menu41',['C03','C05']))
    for id,name,path,func,tasks_ in ui_surfaces:
        if closure_path!=CLOSURE and id in ['hud','growth','inventory']:
            path='chapter1/view/ui38/chapter_hud_quality38.gd'
            func={'hud':'setup','growth':'_growth_cards38','inventory':'_inventory'}[id]
        if UI40_FILE in packaged and id in ['hud','stash','objective']:
            path=UI40_FILE;func={'hud':'setup','stash':'_build_stash','objective':'sync'}[id]
        t=read(path);match=re.search(r'^func '+re.escape(func)+r'\(',t,re.M)
        if match: entity('ui:'+id,name,'ui','ui_surface',path,t[:match.start()].count('\n')+1,{'function':func},task_ids=tasks_)
        else: warnings.append('UI 원본 함수를 찾지 못했습니다: '+path+' / '+func)
    for id,name,path,func in [
        ('arc','번개 연결과 잔광','chapter1/view/chapter_elements_quality14.gd','_sync_arcs'),
        ('ice','빙결 결정','chapter1/view/chapter_elements_quality14.gd','_sync_ice'),
        ('shatter','파쇄 파편','chapter1/view/chapter_elements_quality14.gd','_sync_fragments'),
        ('stun','스턴 궤도 불꽃','chapter1/view/chapter_elements_quality36.gd','sync')]:
        if 'chapter1/view/chapter_elements_quality39.gd' in packaged and id in ['ice','shatter']: path='chapter1/view/chapter_elements_quality39.gd'
        t=read(path);match=re.search(r'^func '+re.escape(func)+r'\(',t,re.M)
        if match:
            effect_row=entity('effects:'+id,name,'effects','visual_effect',path,t[:match.start()].count('\n')+1,{'function':func},task_ids=['V01','V03' if id in ['ice','shatter'] else 'V04'])
            if id=='arc' and ARC44_FILES.issubset(packaged):
                effect_row['assets']=sorted(ARC44_FILES-{'chapter1/view/chapter_elements_quality44.gd'})
                effect_row['attributes']['presentation']='번개44 중심선·잔광·짧은 명중, 실제segments/스턴 유지'
                effect_row['evidence'].append({'path':'chapter1/view/chapter_elements_quality44.gd','line':3,'note':'현재 번개 재질 연결, 실제 경로 계산은14/36 상속'})
    if FIRE43_FILES.issubset(packaged):
        entity('effects:ember','화염 발사·명중·잔화','effects','visual_effect','chapter1/view/chapter_elements_quality43.gd',4,{'function':'setup','scope':'기존 실제 이벤트·배치·수명 유지, 재질3개 교체','damage_owner':False},sorted(FIRE43_FILES-{'chapter1/view/chapter_elements_quality43.gd'}),['V01','V02'])
    portrait_asset=PORTRAIT_DIR+'/ASSET.json';portrait_attribution=PORTRAIT_DIR+'/ATTRIBUTION.ko.md'
    if (ROOT/portrait_asset).is_file() and (ROOT/PORTRAIT_PNG).is_file():
        try:
            portrait_doc=json.loads(read(portrait_asset));attribution_text=read(portrait_attribution)
            portrait_in_use=UI41_FILE in packaged and PORTRAIT_PNG in active
            integration_status='후보41 타이틀 메뉴에서 사용 · 2D' if portrait_in_use else '계획 · 미UI 반영'
            preview_note=('후보41 타이틀 메뉴에 연결된 2D 원화입니다. 현재 주인공 GLB·리그·애니메이션은 교체하지 않았습니다. creation_snapshot은 생성 당시의 기록이며 현재 사용 상태와 구분합니다.' if portrait_in_use else '생성·시각 확인된 2D 초상 원화입니다. 현재 주인공 GLB·리그·애니메이션을 교체하지 않았고 제품 UI에도 연결하지 않았습니다.')
            attributes={'asset_kind':'타이틀 원화 · 2D' if portrait_in_use else '2D 초상 원화','generation_type':'AI-generated','integration_status':integration_status,'not_3d':True,'not_runtime_hero':True,'preview_note':preview_note,'creation_snapshot':{'generation_metadata':portrait_doc,'attribution_text':attribution_text}}
            row=entity('asset:'+PORTRAIT_PNG,'서약의 마녀 · 타이틀 원화(2D)' if portrait_in_use else '서약의 마녀 · 초상 원화(계획)','assets','png',portrait_asset,1,attributes,[PORTRAIT_PNG],['C03','C05'])
            row['usage']=usage(PORTRAIT_PNG);row['dependencies']=[portrait_asset,portrait_attribution,PORTRAIT_DIR+'/PROMPT.txt']
            row['provenance']={'kind':'AI-generated','note':portrait_doc.get('generation','OpenAI image_gen 생성 원화')}
            row['evidence'].append({'path':portrait_attribution,'line':1,'note':'생성 당시 출처·시각 확인 기록(현재 사용 상태는 integration_status 참조)'})
            if portrait_in_use:
                menu=texts[UI41_FILE];match=re.search(r'^func _build_menu41\(',menu,re.M)
                row['evidence'].append({'path':UI41_FILE,'line':menu[:match.start()].count('\n')+1 if match else 1,'note':'후보41 타이틀 메뉴 연결 · 2D 원화 · 3D 모델 미교체'})
        except (OSError,ValueError) as e: warnings.append('초상 원화 출처를 읽지 못했습니다: '+str(e))
    inventory=set(source_paths)
    for folder in ['assets','chapter1/art']:
        inventory.update(p.relative_to(ROOT).as_posix() for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix.lower() not in ('.import','.uid') and '.godot' not in p.parts)
    for p in sorted(inventory):
        full=ROOT/p
        if not full.is_file(): warnings.append('원본 파일 누락: '+p);continue
        license_paths=[x.relative_to(ROOT).as_posix() for x in full.parent.glob('*') if x.is_file() and ('license' in x.name.lower() or 'attribution' in x.name.lower())]
        files.append({'id':'file:'+p,'path':p,'extension':full.suffix.lower(),'bytes':full.stat().st_size,'usage':usage(p),'license':license_paths,'packaged':p in packaged})
        if p!=PORTRAIT_PNG and full.suffix.lower() in ('.png','.svg','.glb','.wav'):
            attrs={'bytes':full.stat().st_size,'license_paths':license_paths}
            if full.suffix.lower()=='.glb':
                try: attrs.update(glb_metadata(full))
                except (OSError,ValueError,KeyError,IndexError,struct.error) as e: warnings.append('GLB 메타데이터 확인 실패 '+p+': '+str(e))
            entity('asset:'+p,full.name,'assets',full.suffix[1:].lower(),p,1,attrs,[p])
    # Captured evidence is separate from shipped game assets and their counts.
    previews={}
    if FIRE43_FILES.issubset(packaged):
        fire=[{'path':'plans/chapter1-quality04-20261101-01/ember43/proof02/compare720/43-explosion-tick657.png','name':'화염 명중·폭발','scope':'화염43 실제 고정 입력 검증 장면 · 정지 이미지'}, {'path':'plans/chapter1-quality04-20261101-01/ember43/proof02/compare720/43-afterglow-tick668.png','name':'짧은 잔화와 투사체','scope':'화염43 실제 고정 입력 검증 장면 · 현재 표현에 상속'}]
        for key in ['effects:ember','skills:chapter1.skill.ember']:previews[key]=fire
    if ARC44_FILES.issubset(packaged):
        arc=[{'path':'plans/chapter1-quality04-20261101-01/arc44/proof/compare1080/44-three_branch-tick1927.png','name':'실제 세 갈래 전류','scope':'번개44 자연 발생 분기 · 실제segments · 정지 이미지'}, {'path':'plans/chapter1-quality04-20261101-01/arc44/proof/compare720/44-stun-tick714.png','name':'연결과 스턴 표시','scope':'번개44 실제 고정 입력 검증 장면 · 금색 스턴 표시 유지'}]
        for key in ['effects:arc','skills:chapter1.skill.arc']:previews[key]=arc
        previews['effects:stun']=[arc[1]]
    if FX39_FILES.issubset(packaged):
        cold=[{'path':'plans/chapter1-quality04-20261101-01/frost39/verify01/captures/39-hit-tick18.png','name':'서리창 실제 명중','scope':'냉기39 실제 고정 입력 검증 장면 · 현재 표현에 상속'}, {'path':'plans/chapter1-quality04-20261101-01/frost39/verify01/captures/39-shatter-tick3577.png','name':'실제 파쇄','scope':'냉기39 실제 파쇄 이벤트 · 정지 이미지'}]
        previews['skills:chapter1.skill.frost']=cold
        previews['effects:ice']=[{'path':'plans/chapter1-quality04-20261101-01/frost39/verify01/frozen-fixture02/39-frozen-fixture.png','name':'빙결 결정','scope':'냉기39 분리 조건 검증 장면 · 일반 플레이 영상과 구분'}]
        previews['effects:shatter']=[cold[1]]
    for row in entities:
        row_previews=[]
        for item in previews.get(row['id'],[]):
            p=(ROOT/item['path']).resolve()
            if p.is_relative_to(ROOT.resolve()) and p.is_file():row_previews.append(item)
        if row_previews:row['previews']=row_previews
    tasks=[];taskpath=PLAN+'/IMPROVEMENT-BACKLOG.ko.md'
    for n,line in enumerate(read(taskpath).splitlines(),1):
        m=re.match(r'\| ([SUVLCGX]\d{2}) \| ([^|]+) \| ([^|]+) \|',line)
        if m:
            id,name,note=m.groups();tasks.append({'id':id,'name':name.strip(),'description':note.strip(),'status':'deferred' if id.startswith('S') else ('review' if id in ['U01','U02','U03','U04'] else ('in_progress' if id in ['V01','V03','U05','U06','U08'] else 'todo')),'priority':'low' if id.startswith('S') else ('high' if id.startswith('U') else 'normal'),'source':{'path':taskpath,'line':n},'entity_ids':[e['id'] for e in entities if id in e['task_ids']]})
    preserved_builds=[{'id':json.loads(read(CLOSURE))['build_id'],'source':CLOSURE,'runtime_file_count':163}]
    selected_number=next((spec['number'] for spec in CANDIDATES if closure_path==spec['directory']+'/closure.json'),37)
    for spec in reversed(CANDIDATES):
        previous_path=spec['directory']+'/closure.json'
        if spec['number']<selected_number and (ROOT/previous_path).is_file():
            previous=json.loads(read(previous_path))
            preserved_builds.insert(0,{'id':previous['build_id'],'source':previous_path,'runtime_file_count':len(previous['runtime_source_files'])})
    performance_passed=False
    if selected_number in [42,43,44]:
        session=f'plans/chapter1-quality04-20261101-01/final-performance{selected_number}/sessions/final-20261113-a/'
        try:
            summary=json.loads(read(session+'three-run-summary.json'))
            binding=json.loads(read(session+'session-bind.json'))
            audits=summary['audits']
            performance_passed=(summary['same_exe'] and summary['fresh_reaudit_matches_saved'] and summary['three_distinct_runtime_identities'] and summary['same_observers'] and summary['same_frozen_payload_and_user_pins'] and summary['eligible_three_runs'] and summary['target_met_all_three'] and len(audits)==3 and all(a['valid'] and a['target_met_for_this_run'] and a['p95_ms']<=16.67 for a in audits) and binding['preservation']['exe_sha256']==build_info['sha256'])
        except (OSError,ValueError,KeyError,TypeError):pass
    if selected_number in [42,43,44]:
        improvement='번개·화염 시각 개선 제공' if selected_number==44 else ('화염 시각 개선 제공' if selected_number==43 else '배우 처리 개선 제공')
        performance_status='대표 부하 성능3회 통과' if performance_passed else '최종 성능 확인 중'
        current_work=f'후보{selected_number} {improvement} · {performance_status} · 전체 수동 완주 미완료'
    else:current_work=('후보41 타이틀 원화 제공 · 최종 관문 확인' if UI41_FILE in packaged else ('후보40 통합 제공 · UI41 초상 메뉴 검증 중 · 제품 미채택' if UI40_FILE in packaged else '냉기39·UI40 검증 완료 · 제품 미채택'))
    verification_names=['pck-audit.json','PACKAGED-INTEGRATION.json','packaged-integration-execution.json']+(['FINAL-PRESERVATION.json'] if UI41_FILE in packaged else [])
    warnings.extend(['패키지 포함만으로 모든 에셋의 실제 화면 사용이 입증되지는 않습니다.','캐릭터·적의 아틀라스는 보존된 역할 정의입니다. 현재 3D 외형은 연결된 배우 구현의 상속·조건 근거를 함께 확인하세요.','관리 상태의 완료는 게임 플레이 품질 검수 완료를 뜻하지 않습니다.'])
    return {'schema_version':1,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'build':{'id':closure['build_id'],'source':closure_path,'entry_scene':entry,'verification_sources':([str(Path(closure_path).parent).replace('\\','/')+'/'+name for name in verification_names] if closure_path!=CLOSURE else []),'preserved_builds':preserved_builds,'runtime_file_count':len(packaged),'executable':build_info['exe'],'launch_instructions':'선택된 후보 실행 파일을 Windows 탐색기에서 실행하세요. 제작실은 게임을 자동 실행하지 않습니다.','scope':closure.get('scope',''),'legacy_book':BOOK+'/index.html','current_work':current_work,'audio_status':'deferred'},'goal':{'title':'보이는 품질과 전체 요소 관리','source':{'path':'PROJECT-GOAL.ko.md','line':1},'text':read('PROJECT-GOAL.ko.md'),'current_work':current_work,'audio_status':'deferred'},'entities':entities,'files':files,'tasks':tasks,'coverage':{'runtime_files':len(packaged),'runtime_extensions':dict(collections.Counter(Path(p).suffix for p in packaged)),'inventory_files':len(files),'entities':len(entities),'categories':dict(collections.Counter(e['category'] for e in entities)),'tasks':len(tasks),'active_source_paths':len(active),'semantic_counts':{'bases':sum(e['type']=='bases' for e in entities),'affixes':sum(e['type']=='affixes' for e in entities),'uniques':sum(e['type']=='uniques' for e in entities),'limits':sum(e['type']=='limits' for e in entities),'skills':len(doc['skills']),'passives':len(doc['passives']),'zones':len(names),'rituals':len(rituals),'audio_variants':sum(counts.values())}},'warnings':warnings}

if __name__=='__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(generate(),ensure_ascii=False,indent=2))
