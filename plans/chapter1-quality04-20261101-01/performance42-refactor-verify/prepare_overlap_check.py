from pathlib import Path

stage=Path('C:/Project/game-research/build-staging/actor42-overlap-exact01')
p=stage/'count42.gd'
text=p.read_text(encoding='utf-8').replace('var calls42 := 0','var result_hits42 := 0\nvar calls42 := 0')
text=text.replace(' calls42+=1',' calls42+=1\n if _overlap42_active and _overlap42_results.has(actor.get_instance_id()):result_hits42+=1')
# This is a diagnostic-only counter file, never a production source.
p.write_text(text,encoding='utf-8')
text=(stage/'cache.gd').read_text(encoding='utf-8')
text=text.replace(' candidate.reset()', ' assert(candidate.result_hits42>0,"Repeated actor query cache must be exercised")\n assert(candidate._overlap42_results.is_empty(),"Results must not escape sync")\n print("RESULT_CACHE_PASS hits=",candidate.result_hits42)\n candidate.reset()')
with (stage/'resultcache.gd').open('x',encoding='utf-8') as f:f.write(text)
print('Prepared result cache exercise')
