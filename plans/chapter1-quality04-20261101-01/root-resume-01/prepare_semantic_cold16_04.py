from pathlib import Path
import shutil
ROOT=Path('C:/Project/d2r-combat-baseline');HERE=Path(__file__).parent;OUT=ROOT/'plans/chapter1-quality04-20261101-01/cold16/semantic03'
shutil.copy2(HERE/'semantic_cold16_03.gd',OUT/'probe-before-explicit-type.gd')
s=(HERE/'semantic_cold16_03.gd').read_text(encoding='utf-8').replace('var before := run.snapshot()','var before: Dictionary=run.snapshot()').replace('cold16/semantic03/result.json','cold16/semantic04/result.json')
p=HERE/'semantic_cold16_04.gd';assert not p.exists();p.write_text(s,encoding='utf-8')
s=(HERE/'run_semantic_cold16_03.py').read_text(encoding='utf-8').replace('cold16/semantic03','cold16/semantic04').replace('semantic_cold16_03.gd','semantic_cold16_04.gd')
p=HERE/'run_semantic_cold16_04.py';assert not p.exists();p.write_text(s,encoding='utf-8');print(str(p))
(OUT/'FAILURE.ko.md').write_text('追加probeのrun.snapshot()はRefCounted経由でVariantなのでvar before:=の型推論がParseErrorだった。原実行/修正前probeを保存しDictionary型を明記したsemantic04へ進む。製品core16/HUD16/FX16はこの修正で変更しない。prototype02の16検査/3主力pacingは別の通過証拠。\n',encoding='utf-8')
