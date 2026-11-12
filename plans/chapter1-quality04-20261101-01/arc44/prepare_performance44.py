from pathlib import Path
import ast

here=Path(__file__).resolve().parent;source=here.parent/'final-performance43';target=here.parent/'final-performance44'
assert not target.exists();target.mkdir()
text=(source/'run_performance43.py').read_text(encoding='utf-8')
changes=[('chapter1-full-candidate-20261113-43','chapter1-full-candidate-20261113-44'),("FULL=SCRIPT.parent/'full43'","FULL=SCRIPT.parent/'full44'"),('frame_probe_render43.gd','frame_probe_render44.gd'),('performance43_observer.gd','performance44_observer.gd'),('performance43-dir','performance44-dir'),('AshenCloisterChapterOneQuality43/','AshenCloisterChapterOneQuality44/'),('Selected43','Selected44'),('approved43','approved44'),('actual43','actual44'),('==180','==183'),('==182','==185'),('the180 runtime','the183 runtime'),('Frozen43','Frozen44'),('Candidate43','Candidate44'),('candidate43','candidate44'),('quality43-','quality44-'),("SCRIPT.parent/'full41',SCRIPT.parent/'full42']:","SCRIPT.parent/'full41',SCRIPT.parent/'full42',SCRIPT.parent/'full43']:"),("post['fx_script']=='res://chapter1/view/chapter_elements_quality43.gd'","post['fx_script']=='res://chapter1/view/chapter_elements_quality44.gd'")]
for old,new in changes:
    assert old in text,old;text=text.replace(old,new)
marker='    assert required.issubset(paths)'
text=text.replace(marker,"    required|={'chapter1/view/chapter_elements_quality44.gd'}|{'chapter1/view/arc_'+part+'_quality44.gdshader' for part in ['core','contact']}\n"+marker)
ast.parse(text)
with (target/'run_performance44.py').open('x',encoding='utf-8') as output:output.write(text)
with (target/'frame_probe_render44.gd').open('x',encoding='utf-8') as output:output.write((source/'frame_probe_render43.gd').read_text(encoding='utf-8'))
observer=(source/'performance43_observer.gd').read_text(encoding='utf-8').replace('final-performance43/frame_probe_render43.gd','final-performance44/frame_probe_render44.gd').replace('performance43-dir','performance44-dir').replace('PERFORMANCE43','PERFORMANCE44').replace('Actual43','Actual44')
with (target/'performance44_observer.gd').open('x',encoding='utf-8') as output:output.write(observer)
print('Prepared44 final gate; no engine/bind/run')
