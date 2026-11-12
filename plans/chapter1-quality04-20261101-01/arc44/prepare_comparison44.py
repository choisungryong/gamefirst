"""Reuse the fire comparison protocol with explicit arc-only observations."""
from pathlib import Path
import ast

here=Path(__file__).resolve().parent
prior=here.parent/'ember43'
text=(prior/'compare43.gd').read_text(encoding='utf-8')
text=text.replace('--ember43-','--arc44-').replace('EMBER43','ARC44').replace('[39,43]','[43,44]').replace('variant==43','variant==44').replace('chapter_elements_quality43.gd','chapter_elements_quality44.gd').replace('chapter1.skill.ember','chapter1.skill.arc')
text=text.replace('var counts := {"cast":0,"hit":0,"explosion":0,"death":0}','var counts := {"cast":0,"hit":0,"death":0,"segments":0,"branch_casts":0,"stunned_frames":0}')
marker='\t\t\t\tif counts.has(event.type):'
assert marker in text
text=text.replace(marker,'''\t\t\t\tif event.type=="cast":
\t\t\t\t\tvar origins := {}
\t\t\t\t\tvar branched := false
\t\t\t\t\tfor segment in event.get("segments",[]):
\t\t\t\t\t\tcounts.segments+=1
\t\t\t\t\t\tif origins.has(segment.from):branched=true
\t\t\t\t\t\torigins[segment.from]=true
\t\t\t\t\tif branched:counts.branch_casts+=1
'''+marker)
start=text.index('\t\t\tif capture.is_empty() and view.run.tick==6')
end=text.index('\t\t\tif not pause_checked',start)
text=text[:start]+'''\t\t\tif view.effects.stun36_visible>0:
\t\t\t\tcounts.stunned_frames+=1
\t\t\t\tif capture.is_empty() and not captures.has("stun") and counts.stunned_frames>5:capture="stun"
\t\t\tif capture.is_empty() and not captures.has("afterglow"):
\t\t\t\tfor link in view.effects.arc_links:
\t\t\t\t\tif link.age/link.duration>.40 and link.age/link.duration<.80:capture="afterglow";break
'''+text[end:]
text=text.replace('"ice_fragments":effects.ice_fragments','"ice_fragments":effects.ice_fragments,"stun_visible":effects.stun36_visible')
text=text.replace('no performance/full-win/evolved explosion claim unless observed','no performance/full-win/three-branch claim unless observed')
with (here/'compare44.gd').open('x',encoding='utf-8') as output:output.write(text)
runner=(prior/'run43.py').read_text(encoding='utf-8')
runner=runner.replace('ember43-preview','arc44-preview').replace('final42','final43').replace('final-performance42/run_performance42.py','final-performance43/run_performance43.py').replace("full42/closure.json","full43/closure.json").replace('compare43.gd','compare44.gd').replace('--ember43-','--arc44-').replace('AshenCloisterChapterOneQuality42','AshenCloisterChapterOneQuality43').replace('AshenCloisterDiagnosticEmber43','AshenCloisterDiagnosticArc44')
old="['chapter1/view/chapter_elements_quality43.gd','chapter1/view/ember_core_quality43.gdshader','chapter1/view/ember_afterglow_quality43.gdshader','chapter1/view/ember_contact_quality43.gdshader']"
new="['chapter1/view/chapter_elements_quality44.gd','chapter1/view/arc_core_quality44.gdshader','chapter1/view/arc_contact_quality44.gdshader']"
assert old in runner;runner=runner.replace(old,new)
ast.parse(runner)
with (here/'run44.py').open('x',encoding='utf-8') as output:output.write(runner)
print('Prepared explicit arc44 comparison and runner')
