from pathlib import Path
H=Path(__file__).parent
s=(H/'actor28_mapped.gd').read_text(encoding='utf-8').replace('"attack_kind":e.attack_kind,"position":e.position','"attack_kind":e.attack_kind,"kind":e.kind,"position":e.position')
p=H/'actor28_mapped02.gd';assert not p.exists();p.write_text(s,encoding='utf-8')
s=(H/'run_actor28_mapped01.py').read_text(encoding='utf-8').replace('actor28/mapped01','actor28/mapped02').replace('chapter1-actor28-mapped01','chapter1-actor28-mapped02').replace("H/'actor28_mapped.gd'","H/'actor28_mapped02.gd'")
p=H/'run_actor28_mapped02_generated.py';assert not p.exists();p.write_text(s,encoding='utf-8');exec(compile(s,str(p),'exec'))
