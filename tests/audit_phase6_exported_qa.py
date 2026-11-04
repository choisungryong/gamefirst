"""Read-only independent phase6 frozen-source and exported-QA artifact audit."""
from pathlib import Path
import hashlib, json, struct, sys

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'evidence/phase6/builds/phase6-candidate-20261030-01'
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def audit(directory):
    failures=[]
    def require(ok, message):
        if not ok: failures.append(message)
    receipt=read(BUILD/'build.json')
    mapping=read(BUILD/'source-manifest.json')
    require(len(mapping)==receipt['source_count']==32, 'Frozen product count')
    for name,digest in mapping.items():
        require(sha(ROOT/name)==digest, 'Current source differs: '+name)
        require(sha(BUILD/'source'/name)==digest, 'Snapshot source differs: '+name)
    require(sha(Path(receipt['exe']))==receipt['exe_sha256'], 'Executable hash changed')
    require(mapping['game_data/build_info.json']==receipt['metadata_sha256'], 'Build metadata pin')
    metadata=read(BUILD/'source/game_data/build_info.json')
    expected_map={k:v for k,v in mapping.items() if k!='game_data/build_info.json'}
    require(metadata['source_hashes']==expected_map, 'Metadata source map')
    old_oracle=read(ROOT/'evidence/phase5/verification/frozen-fingerprint-oracle-20261030.json')
    for key in ['catalog','equipment']:
        require(mapping['game_data/'+key+'.json']==old_oracle[key+'_sha256'], 'Historical oracle definition remains identical: '+key)
    catalog=read(BUILD/'source/game_data/catalog.json')
    equipment=read(BUILD/'source/game_data/equipment.json')
    bases={d['id']:d for d in equipment['items']}
    affixes={d['id']:d for d in equipment['affixes']}
    stats={d['id']:d for d in catalog['stats']}
    receipts=read(directory/'qa-receipts.json')
    require(len(receipts)==2, 'Two resolution receipts')
    cases=[]
    for width,height in [(1440,810),(1920,1080)]:
        label=f'{width}x{height}'; case=directory/label
        report=read(case/'qa-report.json'); launch=read(directory/(label+'-launch.json'))
        actual=next(r for r in receipts if r['dimensions']==[width,height])
        require(actual['actual_exit']==0 and actual['stderr_bytes']==0, label+' actual exit/stderr')
        require(report['success'] is True and report['failures']==[] and report['checks']==actual['checks']==52, label+' checks (final TTL/node QA)')
        require(report['metadata_sha256']==launch['metadata_sha256']==receipt['metadata_sha256'], label+' metadata pin')
        require(report['metadata']==metadata, label+' embedded source metadata')
        require(report['external_script_sha256']==launch['external_script_sha256']==sha(ROOT/'tests/phase6_exported_qa.gd'),label+' harness pin')
        require(report['display_server']!='headless' and report['renderer']=='forward_plus',label+' GPU mode')
        require(Path(report['executable']).resolve()==Path(receipt['exe']).resolve() and launch['exe_sha256']==receipt['exe_sha256'],label+' executable identity')
        require(report['original_source_text_present'] is False,label+' remapped scripts')
        require(report['native_progress_before']==report['native_progress_after']=='absent',label+' actual progress save untouched')
        require(report['normal_user_save_before']==report['normal_user_save_after']=='b376f88d6db4c443332908f5cf09860a4eda24701cbefb25c9cbd8289e202353',label+' actual equipment save untouched')
        save=Path(report['isolated_save_path'])
        require(save.resolve().is_relative_to(Path(receipt['exe']).parent.resolve()/'evidence/phase6'),label+' isolated save containment')
        require(sha(save)==report['isolated_save_sha256'],label+' isolated save bytes')
        saved=read(save)
        require(saved['xp']==6 and len(saved['ground'])==2,label+' saved real-kill rewards')
        require(saved['equipment']['equipped']=={'focus':1,'body':2},label+' saved gear')
        require(saved['equipment']['catalog_sha256']==old_oracle['equipment_content_fingerprint'],label+' equipment fingerprint')
        final=report['final']; inventory=final['equipment']; owned={int(i['uid']):i for i in inventory['items']}
        require(len(owned)==len(inventory['items'])==5 and inventory['next_uid']==38,label+' shared UID/ownership final')
        require(final['progress']['xp']==141 and final['progress']['ground']==[],label+' synthetic cap/reset fixture final')
        values={key:int(spec.get('default_raw',0)) for key,spec in stats.items()}
        player=catalog['player']
        values[player['health_stat_id']]=player['max_health_raw']; values[player['mana_stat_id']]=player['max_mana_raw']
        adds={key:0 for key in values}; percents={key:0 for key in values}
        for slot,uid in inventory['equipped'].items():
            item=owned[uid]; base=bases[item['base_id']]
            require(base['slot']==slot and base['minimum_level']<=3,label+' requirement/slot')
            modifiers=list(base['base_modifiers'])
            for affix in item['affixes']:
                spec=affixes[affix['id']]['modifier']
                require(affix['id'] in base['affix_ids'] and spec['minimum']<=affix['value']<=spec['maximum'] and (affix['value']-spec['minimum'])%spec['step']==0,label+' affix range/step')
                modifiers.append({'stat_id':spec['stat_id'],'operation':spec['operation'],'value':affix['value']})
            for modifier in modifiers:
                (adds if modifier['operation']=='add' else percents)[modifier['stat_id']]+=int(modifier['value'])
        for key,spec in stats.items():
            values[key]=min(int(spec.get('maximum_raw',2147483647)),max(int(spec.get('minimum_raw',0)),(values[key]+adds[key])*max(0,10000+percents[key])//10000))
        require(final['stats']==values,label+' independent derived stats')
        require(final['life']*256==final['life_max_raw']==values[player['health_stat_id']] and final['mana_raw']==values[player['mana_stat_id']],label+' explicit reset maxima')
        skill=next(d for d in catalog['skills'] if d['id']==catalog['experiment']['skill_id'])
        bonus=min(20,max(0,values[skill['bonus_curve']['stat_id']]))
        for edge in ['min','max']:
            raw=(skill['damage'][edge+'_raw']+bonus*skill['bonus_curve'][edge+'_per_bonus_raw'])*(10000+values['stat.spell_power'])//10000
            require(final['skill']['damage_'+edge+'_raw']==raw,label+' independent skill '+edge)
        require(len(report['captures'])==9,label+' capture count')
        for capture in report['captures']:
            path=Path(capture['path']); blob=path.read_bytes()
            require(path.resolve().is_relative_to(case.resolve()) and sha(path)==capture['sha256'],label+' capture path/hash')
            require(blob[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',blob[16:24])==(width,height)==tuple(capture['dimensions']),label+' actual PNG framebuffer')
        cases.append({'dimensions':[width,height],'checks':report['checks'],'captures':len(report['captures']),'save_sha256':report['isolated_save_sha256'],'synthetic_final_xp':final['progress']['xp']})
    return {'scope':'Read-only phase6 frozen32/EXE/metadata and exported QA audit; cap fixture is synthetic, not performance or OS input evidence','success':not failures,'failures':failures,'cases':cases,'exe_sha256':receipt['exe_sha256']}

if __name__=='__main__':
    result=audit(Path(sys.argv[1]))
    if len(sys.argv)>2:
        target=Path(sys.argv[2])
        if target.exists(): raise RuntimeError('Preserve previous audit output')
        target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))
    raise SystemExit(0 if result['success'] else 1)
