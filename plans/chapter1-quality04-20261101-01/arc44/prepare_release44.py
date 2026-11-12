from pathlib import Path
import hashlib,json

here=Path(__file__).resolve().parent;root=here.parents[2];release=here.parent/'full44'
results=[]
for size in ['720','1080']:
    result=json.loads((here/'proof'/('compare'+size)/'RESULT.json').read_text(encoding='utf-8'))
    execution=json.loads((here/'proof'/(size+'-execution.json')).read_text(encoding='utf-8'))
    assert result['success'] and result['same_core_hash_chain'] and result['same_presentation_pools']
    assert execution['exit']==0 and not execution['errors'] and execution['preserved']
    results.append(result)
assert results[1]['variants'][1]['counts']['three_branch_casts']>0
assert results[0]['variants'][1]['core_hash_chain']==results[1]['variants'][1]['core_hash_chain']
new=['chapter1/view/chapter_elements_quality44.gd']+['chapter1/view/arc_'+n+'_quality44.gdshader' for n in ['core','contact']]
selection={'visual_review_passed':True,'parity_passed':True,'files':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in new},'scope':'Root inspected720 hit/stun and1080 natural three-way branch; no new damage/events/pools; final performance/manual separate','proofs':[str(here/'proof'/('compare'+s)/'RESULT.json') for s in ['720','1080']]}
for p,h in selection['files'].items():assert hashlib.sha256((Path('C:/Project/game-research/build-staging/arc44-preview01')/p).read_bytes()).hexdigest()==h
with (release/'SELECTION.json').open('x',encoding='utf-8') as output:json.dump(selection,output,ensure_ascii=False,indent=2)
source=(here.parent/'full43/packaged43_integration.gd').read_text(encoding='utf-8')
for old,new in [('AshenCloisterChapterOneQuality43','AshenCloisterChapterOneQuality44'),('--ui43-output=','--ui44-output='),('PACKAGED43','PACKAGED44'),('Actual43','Actual44'),('separate43','separate44'),('const FX43=preload("res://chapter1/view/chapter_elements_quality43.gd")','const FX44=preload("res://chapter1/view/chapter_elements_quality44.gd")'),('"actual FX43 script",view.effects.get_script()==FX43','"actual FX44 script",view.effects.get_script()==FX44'),('"packaged fire contact shader"','"packaged combined fire/arc contact shader"'),('load("res://chapter1/view/ember_contact_quality43.gdshader")','load("res://chapter1/view/arc_contact_quality44.gdshader")')]:
    assert old in source,old;source=source.replace(old,new)
marker='\t_check("actual FX44 script",view.effects.get_script()==FX44)'
source=source.replace(marker,marker+'\n\t_check("packaged arc ribbon shader",view.effects.arc_surface.material_override.shader==load("res://chapter1/view/arc_core_quality44.gdshader"))')
with (release/'packaged44_integration.gd').open('x',encoding='utf-8') as output:output.write(source)
print('Prepared44 selection and integration, natural three-way observed')
