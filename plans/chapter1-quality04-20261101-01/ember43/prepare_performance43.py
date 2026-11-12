"""Copy the already exercised42 gate, changing only43 package contracts."""
from pathlib import Path
import ast

here=Path(__file__).resolve().parent
source=here.parent/'final-performance42';target=here.parent/'final-performance43'
assert not target.exists();target.mkdir()
text=(source/'run_performance42.py').read_text(encoding='utf-8')
for old,new in [
 ('chapter1-full-candidate-20261113-42','chapter1-full-candidate-20261113-43'),
 ("FULL=SCRIPT.parent/'full42'","FULL=SCRIPT.parent/'full43'"),
 ('frame_probe_render42.gd','frame_probe_render43.gd'),
 ('performance42_observer.gd','performance43_observer.gd'),
 ('performance42-dir','performance43-dir'),
 ('AshenCloisterChapterOneQuality42/','AshenCloisterChapterOneQuality43/'),
 ('Selected42','Selected43'),('approved42','approved43'),('actual42','actual43'),
 ('==176','==180'),('==178','==182'),('the176 runtime','the180 runtime'),
 ('Frozen42','Frozen43'),('Candidate42','Candidate43'),('candidate42','candidate43'),
 ('quality42-','quality43-'),
 ("SCRIPT.parent/'full40',SCRIPT.parent/'full41']:","SCRIPT.parent/'full40',SCRIPT.parent/'full41',SCRIPT.parent/'full42']:"),
 ("post['fx_script']=='res://chapter1/view/chapter_elements_quality39.gd'","post['fx_script']=='res://chapter1/view/chapter_elements_quality43.gd'")]:
    assert old in text,old
    text=text.replace(old,new)
marker='    assert required.issubset(paths)'
assert marker in text
text=text.replace(marker,"    required|={'chapter1/view/chapter_elements_quality43.gd'}|{'chapter1/view/ember_'+part+'_quality43.gdshader' for part in ['core','afterglow','contact']}\n"+marker)
ast.parse(text)
with (target/'run_performance43.py').open('x',encoding='utf-8') as output:output.write(text)
with (target/'frame_probe_render43.gd').open('x',encoding='utf-8') as output:output.write((source/'frame_probe_render42.gd').read_text(encoding='utf-8'))
observer=(source/'performance42_observer.gd').read_text(encoding='utf-8').replace('final-performance42/frame_probe_render42.gd','final-performance43/frame_probe_render43.gd').replace('performance42-dir','performance43-dir').replace('PERFORMANCE42','PERFORMANCE43').replace('Actual42','Actual43')
with (target/'performance43_observer.gd').open('x',encoding='utf-8') as output:output.write(observer)
print('Prepared43 gate; no engine/binding/run launched')
