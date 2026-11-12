from pathlib import Path
import hashlib,json

here=Path(__file__).resolve().parent;root=here.parents[2];release=here.parent/'full43'
results=[]
for size in ['720','1080']:
    result=json.loads((here/'proof02'/('compare'+size)/'RESULT.json').read_text(encoding='utf-8'))
    execution=json.loads((here/'proof02'/(size+'-execution.json')).read_text(encoding='utf-8'))
    assert result['success'] and result['same_core_hash_chain'] and result['same_presentation_pools']
    assert execution['exit']==0 and not execution['errors'] and execution['preserved']
    results.append(result)
assert results[0]['variants'][1]['core_hash_chain']==results[1]['variants'][1]['core_hash_chain']
new=['chapter1/view/chapter_elements_quality43.gd']+['chapter1/view/ember_'+n+'_quality43.gdshader' for n in ['core','afterglow','contact']]
selection={'visual_review_passed':True,'parity_passed':True,'files':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in new},'scope':'Root inspected720/1080 actual paid hit/explosion/afterglow; no new damage/events/pools; no final performance/full manual claim','proofs':[str(here/'proof02'/('compare'+s)/'RESULT.json') for s in ['720','1080']]}
for p,h in selection['files'].items():assert hashlib.sha256((Path('C:/Project/game-research/build-staging/ember43-preview02')/p).read_bytes()).hexdigest()==h
with (release/'SELECTION.json').open('x',encoding='utf-8') as output:json.dump(selection,output,ensure_ascii=False,indent=2)
source=(here.parent/'full42/packaged42_integration.gd').read_text(encoding='utf-8')
source=source.replace('AshenCloisterChapterOneQuality42','AshenCloisterChapterOneQuality43').replace('--ui42-output=','--ui43-output=').replace('PACKAGED42','PACKAGED43').replace('Actual42','Actual43').replace('Actual42','Actual43').replace('actual42','actual43').replace('separate42','separate43')
source=source.replace('const FX39=preload("res://chapter1/view/chapter_elements_quality39.gd")','const FX43=preload("res://chapter1/view/chapter_elements_quality43.gd")')
source=source.replace('_check("actual FX39 script",view.effects.get_script()==FX39)','''_check("actual FX43 script",view.effects.get_script()==FX43)
	_check("packaged fire projectile shader",view.effects.projectiles.material_override.shader==load("res://chapter1/view/ember_core_quality43.gdshader"))
	_check("packaged fire afterglow shader",view.effects.plumes.material_override.shader==load("res://chapter1/view/ember_afterglow_quality43.gdshader"))
	_check("packaged fire contact shader",view.effects.contact_batch.material_override.shader==load("res://chapter1/view/ember_contact_quality43.gdshader"))''')
with (release/'packaged43_integration.gd').open('x',encoding='utf-8') as output:output.write(source)
print('Prepared release43 selection and integration fixture')
