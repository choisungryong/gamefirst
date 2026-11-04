from pathlib import Path
H=Path(__file__).parent
s=(H/'run_space27_combat01.py').read_text(encoding='utf-8').replace('space27/combat01','space29/shadow01').replace('chapter1-space27-combat01','chapter1-space29-shadow01').replace('full26','full28').replace('chapter_ground_quality27.gdshader','chapter_world_quality29.gd').replace('space27_combat.gd','space29_shadow_compare.gd').replace('space27-result','space29-result').replace('space27-shots','space29-shots').replace('O.mkdir();','O.mkdir(parents=True);')
p=H/'run_space29_shadow01_generated.py';assert not p.exists();p.write_text(s,encoding='utf-8');exec(compile(s,str(p),'exec'))
