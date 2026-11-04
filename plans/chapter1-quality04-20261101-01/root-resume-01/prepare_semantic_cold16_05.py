from pathlib import Path
import shutil
ROOT=Path('C:/Project/d2r-combat-baseline');HERE=Path(__file__).parent;OUT=ROOT/'plans/chapter1-quality04-20261101-01/cold16/semantic04'
shutil.copy2(HERE/'semantic_cold16_04.gd',OUT/'probe-before-overkill-expectation-fix.gd')
s=(HERE/'semantic_cold16_04.gd').read_text(encoding='utf-8').replace('run.metrics.damage_raw==26*256','run.metrics.damage_raw==42*256').replace('metrics contain only paid direct12 plus secondary14','metrics preserve raw attack28 plus secondary14 including existing overkill semantics').replace('cold16/semantic04/result.json','cold16/semantic05/result.json')
p=HERE/'semantic_cold16_05.gd';assert not p.exists();p.write_text(s,encoding='utf-8')
s=(HERE/'run_semantic_cold16_04.py').read_text(encoding='utf-8').replace('cold16/semantic04','cold16/semantic05').replace('semantic_cold16_04.gd','semantic_cold16_05.gd')
p=HERE/'run_semantic_cold16_05.py';assert not p.exists();p.write_text(s,encoding='utf-8')
(OUT/'EXPECTATION-REVIEW.ko.md').write_text('추가11검사중10개는통과했으나damage_raw를실제HP감소량12+14로가정한검사가실패했다. 기존combat_resolver.gd:10–22는total_raw를피해계산결과로유지하고HP만clamp하므로공격원시값28+14=42가맞다. 과잉피해계측의기존의미를바꾸지않고검사기대만05에서수정한다. 원시04/프로브/결과를보존하며제품core/HUD/FX16은수정하지않았다.\n',encoding='utf-8')
print(str(p))
