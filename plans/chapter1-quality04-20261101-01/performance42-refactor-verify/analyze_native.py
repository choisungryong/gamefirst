from pathlib import Path

here=Path(__file__).resolve().parent
source=(here.parent/'performance42-components/analyze42.py').read_text(encoding='utf-8')
source=source.replace("H=Path(__file__).resolve().parent;R=H/'run04/raw'", "H=Path(__file__).resolve().parent/'native01';R=H/'raw'")
assert not (here/'native01/ANALYSIS.json').exists()
exec(compile(source,str(__file__),'exec'))
