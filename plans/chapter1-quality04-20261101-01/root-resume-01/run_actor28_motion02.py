from pathlib import Path
H=Path(__file__).parent
s=(H/'run_actor28_motion01.py').read_text(encoding='utf-8').replace('actor28/motion01','actor28/motion02').replace('actor28/fixture01','actor28/fixture02')
exec(compile(s,str(H/'run_actor28_motion02.py'),'exec'))
