from pathlib import Path
H=Path(__file__).parent
s=(H/'run_space27_combat01.py').read_text(encoding='utf-8')
s=s.replace('space27/combat01','hud27/fixture01').replace('chapter1-space27-combat01','chapter1-hud27-fixture01')
s=s.replace('O.mkdir();','O.mkdir(parents=True);')
s=s.replace('chapter_ground_quality27.gdshader','chapter_hud_quality27.gd').replace('space27_combat.gd','hud27_fixture.gd')
s=s.replace('space27-result','hud27-result').replace('space27-shots','hud27-shots').replace('SPACE27 COMBAT FIXTURE','HUD27 FIXTURE')
exec(compile(s,str(H/'run_hud27_fixture01.py'),'exec'))
