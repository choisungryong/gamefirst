"""Read-only, bounded source catalog. No Godot execution or arbitrary evaluation."""
from pathlib import Path
import collections, datetime, hashlib, json, re, struct
ROOT = Path(__file__).resolve().parents[2]
PLAN = 'plans/chapter1-presentation-roadmap-20261107-01'
BOOK = 'plans/chapter1-quality04-20261101-01/full30/book-v44/dist'
CLOSURE = 'plans/chapter1-quality04-20261101-01/full37/build/closure.json'
CANDIDATE38 = 'plans/chapter1-quality04-20261101-01/ui38/package38'
UI38_FILES = {'chapter1/view/ui38/chapter_hud_quality38.gd','chapter1/view/ui38/element_seal.gd','chapter1/view/ui38/life_seal.gd'}

def read(path):
    return (ROOT/path).read_text(encoding='utf-8-sig')

def verified_candidate(directory, root=ROOT):
    """Select only a complete successful package, never a partially written build."""
    try:
        folder=root/directory
        closure=json.loads((folder/'closure.json').read_text(encoding='utf-8-sig'))
        build=json.loads((folder/'build.json').read_text(encoding='utf-8-sig'))
        execution=json.loads((folder/'packaged-integration-execution.json').read_text(encoding='utf-8-sig'))
        integration=json.loads((folder/'PACKAGED-INTEGRATION.json').read_text(encoding='utf-8-sig'))
        audit=json.loads((folder/'pck-audit.json').read_text(encoding='utf-8-sig'))
        paths=closure['runtime_source_files']; exe=Path(build['exe'])
        if execution.get('actual_exit')!=0 or execution.get('timed_out',False) or execution.get('launch_error') is not None or integration.get('success') is not True or audit.get('success') is not True: return None
        if len(paths)!=166 or len(set(paths))!=166 or not UI38_FILES.issubset(paths) or build.get('runtime_count',build.get('source_count'))!=166: return None
        if any(not (root/p).is_file() for p in paths): return None
        if not exe.resolve().is_relative_to((root/'builds/chapter1').resolve()) or not exe.is_file() or exe.stat().st_size!=build['bytes']: return None
        if hashlib.sha256(exe.read_bytes()).hexdigest()!=build['sha256']: return None
        return closure,build
    except (OSError,ValueError,KeyError,TypeError):
        return None

def selected_build():
    selected=verified_candidate(CANDIDATE38)
    if selected: return CANDIDATE38+'/closure.json',selected[0],selected[1]
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
    source_paths=packaged|{p for p in UI38_FILES if (ROOT/p).is_file()}
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
        return 'packaged-unproven' if p in packaged else ('plan' if p.startswith(PLAN) or p in UI38_FILES else 'legacy-preserved')
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
    for id,name,path,func,tasks_ in [
        ('hud','전투 HUD','chapter1/view/cloister_hud.gd','setup',['U01','U02']),
        ('growth','성장 선택 카드','chapter1/view/cloister_hud.gd','_build_modal',['U03']),
        ('inventory','장비 비교와 장착','chapter1/view/cloister_hud.gd','_inventory',['U04']),
        ('stash','장비 보관함','chapter1/view/chapter_hud.gd','_build_stash',['U05']),
        ('objective','현재 목표와 의식 안내','chapter1/view/chapter_hud.gd','sync',['U06']),
        ('discovery','희귀 장비 발견 표시','chapter1/view/chapter_hud_quality20.gd','_present_discovery20',['L02'])]:
        if closure_path!=CLOSURE and id in ['hud','growth','inventory']:
            path='chapter1/view/ui38/chapter_hud_quality38.gd'
            func={'hud':'setup','growth':'_growth_cards38','inventory':'_inventory'}[id]
        t=read(path);match=re.search(r'^func '+re.escape(func)+r'\(',t,re.M)
        if match: entity('ui:'+id,name,'ui','ui_surface',path,t[:match.start()].count('\n')+1,{'function':func},task_ids=tasks_)
        else: warnings.append('UI 원본 함수를 찾지 못했습니다: '+path+' / '+func)
    for id,name,path,func in [
        ('arc','번개 연결과 잔광','chapter1/view/chapter_elements_quality14.gd','_sync_arcs'),
        ('ice','빙결 결정','chapter1/view/chapter_elements_quality14.gd','_sync_ice'),
        ('shatter','파쇄 파편','chapter1/view/chapter_elements_quality14.gd','_sync_fragments'),
        ('stun','스턴 궤도 불꽃','chapter1/view/chapter_elements_quality36.gd','sync')]:
        t=read(path);match=re.search(r'^func '+re.escape(func)+r'\(',t,re.M)
        if match: entity('effects:'+id,name,'effects','visual_effect',path,t[:match.start()].count('\n')+1,{'function':func},task_ids=['V01','V03' if id in ['ice','shatter'] else 'V04'])
    inventory=set(source_paths)
    for folder in ['assets','chapter1/art']:
        inventory.update(p.relative_to(ROOT).as_posix() for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix.lower() not in ('.import','.uid') and '.godot' not in p.parts)
    for p in sorted(inventory):
        full=ROOT/p
        if not full.is_file(): warnings.append('원본 파일 누락: '+p);continue
        license_paths=[x.relative_to(ROOT).as_posix() for x in full.parent.glob('*') if x.is_file() and ('license' in x.name.lower() or 'attribution' in x.name.lower())]
        files.append({'id':'file:'+p,'path':p,'extension':full.suffix.lower(),'bytes':full.stat().st_size,'usage':usage(p),'license':license_paths,'packaged':p in packaged})
        if full.suffix.lower() in ('.png','.svg','.glb','.wav'):
            attrs={'bytes':full.stat().st_size,'license_paths':license_paths}
            if full.suffix.lower()=='.glb':
                try: attrs.update(glb_metadata(full))
                except (OSError,ValueError,KeyError,IndexError,struct.error) as e: warnings.append('GLB 메타데이터 확인 실패 '+p+': '+str(e))
            entity('asset:'+p,full.name,'assets',full.suffix[1:].lower(),p,1,attrs,[p])
    tasks=[];taskpath=PLAN+'/IMPROVEMENT-BACKLOG.ko.md'
    for n,line in enumerate(read(taskpath).splitlines(),1):
        m=re.match(r'\| ([SUVLCGX]\d{2}) \| ([^|]+) \| ([^|]+) \|',line)
        if m:
            id,name,note=m.groups();tasks.append({'id':id,'name':name.strip(),'description':note.strip(),'status':'deferred' if id.startswith('S') else ('in_progress' if id in ['U01','U02','U03','U04'] else 'todo'),'priority':'low' if id.startswith('S') else ('high' if id.startswith('U') else 'normal'),'source':{'path':taskpath,'line':n},'entity_ids':[e['id'] for e in entities if id in e['task_ids']]})
    warnings.extend(['패키지 포함만으로 모든 에셋의 실제 화면 사용이 입증되지는 않습니다.','캐릭터·적의 아틀라스는 보존된 역할 정의입니다. 현재 3D 외형은 연결된 배우 구현의 상속·조건 근거를 함께 확인하세요.','관리 상태의 완료는 게임 플레이 품질 검수 완료를 뜻하지 않습니다.'])
    return {'schema_version':1,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'build':{'id':closure['build_id'],'source':closure_path,'entry_scene':entry,'verification_sources':([CANDIDATE38+'/'+name for name in ['pck-audit.json','PACKAGED-INTEGRATION.json','packaged-integration-execution.json']] if closure_path!=CLOSURE else []),'preserved_builds':[{'id':json.loads(read(CLOSURE))['build_id'],'source':CLOSURE,'runtime_file_count':163}],'runtime_file_count':len(packaged),'executable':build_info['exe'],'launch_instructions':'선택된 후보 실행 파일을 Windows 탐색기에서 실행하세요. 제작실은 게임을 자동 실행하지 않습니다.','scope':closure.get('scope',''),'legacy_book':BOOK+'/index.html','current_work':'UI38','audio_status':'deferred'},'goal':{'title':'보이는 품질과 전체 요소 관리','source':{'path':'PROJECT-GOAL.ko.md','line':1},'text':read('PROJECT-GOAL.ko.md'),'current_work':'UI38','audio_status':'deferred'},'entities':entities,'files':files,'tasks':tasks,'coverage':{'runtime_files':len(packaged),'runtime_extensions':dict(collections.Counter(Path(p).suffix for p in packaged)),'inventory_files':len(files),'entities':len(entities),'categories':dict(collections.Counter(e['category'] for e in entities)),'tasks':len(tasks),'active_source_paths':len(active),'semantic_counts':{'bases':sum(e['type']=='bases' for e in entities),'affixes':sum(e['type']=='affixes' for e in entities),'uniques':sum(e['type']=='uniques' for e in entities),'limits':sum(e['type']=='limits' for e in entities),'skills':len(doc['skills']),'passives':len(doc['passives']),'zones':len(names),'rituals':len(rituals),'audio_variants':sum(counts.values())}},'warnings':warnings}

if __name__=='__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(generate(),ensure_ascii=False,indent=2))
