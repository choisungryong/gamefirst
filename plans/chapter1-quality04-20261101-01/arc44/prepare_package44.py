"""Prepare a separate44 packager; keep the exercised43 helper unchanged."""
from pathlib import Path
import ast

here=Path(__file__).resolve().parent
target=here.parent/'full44';assert not target.exists();target.mkdir()
text=(here.parent/'full43/package43.py').read_text(encoding='utf-8')
changes=[
 ('Fire43 package','Arc44 package'),
 ("OLD=HERE.parent/'full42'","OLD=HERE.parent/'full43'"),
 ('chapter1-full-candidate-20261113-43','chapter1-full-candidate-20261113-44'),
 ('chapter1-before43-20261113-01','chapter1-before44-20261113-01'),
 ("USER43=Path(os.environ['APPDATA'])/'AshenCloisterChapterOneQuality43'","USER44=Path(os.environ['APPDATA'])/'AshenCloisterChapterOneQuality44'"),
 ("USER42=Path(os.environ['APPDATA'])/'AshenCloisterChapterOneQuality42'","USER43=Path(os.environ['APPDATA'])/'AshenCloisterChapterOneQuality43'"),
 ("NEW=['chapter1/view/chapter_elements_quality43.gd']+['chapter1/view/ember_'+n+'_quality43.gdshader' for n in ['core','afterglow','contact']]","NEW=['chapter1/view/chapter_elements_quality44.gd']+['chapter1/view/arc_'+n+'_quality44.gdshader' for n in ['core','contact']]"),
 ("old=module('package42',OLD/'package42.py')","old=module('package42',HERE.parent/'full42/package42.py')"),
 ("previous=module('final42',HERE.parent/'final-performance42/run_performance42.py')","previous=module('final43',HERE.parent/'final-performance43/run_performance43.py')"),
 ('==180','==183'),("'runtime_count':180","'runtime_count':183"),("'source_count':180","'source_count':183"),("'stage_count':182","'stage_count':185"),
 ('unchanged_root42','unchanged_root43'),
 ('chapter1-full-candidate-20261113-42/AshenCloister-Chapter1.exe','chapter1-full-candidate-20261113-43/AshenCloister-Chapter1.exe'),
 ('ROOT42-BEFORE','ROOT43-BEFORE'),
 ('[STAGE,OUT,USER43,BACKUP]','[STAGE,OUT,USER44,BACKUP]'),
 ('USER43.mkdir()','USER44.mkdir()'),('USER42.glob','USER43.glob'),('target=USER43/source.name','target=USER44/source.name'),("(USER43/'chapter-one-profile-v1.json')","(USER44/'chapter-one-profile-v1.json')"),
 ("source=b'res://chapter1/view/chapter_elements_quality39.gd'","source=b'res://chapter1/view/chapter_elements_quality43.gd'"),
 ("target=b'res://chapter1/view/chapter_elements_quality43.gd'","target=b'res://chapter1/view/chapter_elements_quality44.gd'"),
 ('current42_forked_once','current43_forked_once'),('ADOPTED43','ADOPTED44'),
 ("replace('Quality42','Quality43')","replace('Quality43','Quality44')"),
 ("replace('ChapterOne Quality42 Windows','ChapterOne Quality43 Windows')","replace('ChapterOne Quality43 Windows','ChapterOne Quality44 Windows')"),
 ("'--export-release','ChapterOne Quality43 Windows',exe]","'--export-release','ChapterOne Quality44 Windows',exe]"),
 ('Fire43 three shader replacements; Actor42/HUD41/Core37/cold39/audio/models unchanged','Arc44 two shader replacements; Fire43/Actor42/HUD41/Core37/cold39/audio/models unchanged'),
 ('Fire43 presentation; final performance/full manual completion separate','Arc44 presentation; final performance/full manual completion separate'),
 ('packaged43_integration.gd','packaged44_integration.gd'),('--ui43-output=','--ui44-output='),('source43_and_stage43_unchanged','source44_and_stage44_unchanged')]
for old,new in changes:
    assert old in text,old
    text=text.replace(old,new)
ast.parse(text)
with (target/'package44.py').open('x',encoding='utf-8') as output:output.write(text)
print('Prepared44 packager only; no adoption/build/run')
