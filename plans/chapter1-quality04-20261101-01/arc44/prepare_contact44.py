from pathlib import Path

root=Path(__file__).resolve().parents[3]
source=(root/'chapter1/view/ember_contact_quality43.gdshader').read_text(encoding='utf-8')
assert source.rstrip().endswith('}')
branch='''
 // A short kink at the actual arc contact. Existing fire/cold paths stay above.
 if(data.g>.75){
  float kink=abs(p.x-.035)*.34-.045;
  float thread=(1.-smoothstep(.022,.060,abs(p.y-kink)))*(1.-smoothstep(.30,.52,abs(p.x)));
  float center43=exp(-dot(p,p)*120.);
  float fade44=pow(1.-age,1.8);
  ALBEDO=(vec3(.79,.88,1.)*thread*1.7+vec3(.28,.42,1.)*center43*.55)*fade44;
  ALPHA=clamp((thread+center43*.35)*fade44,0.,1.);
 }
'''
with (root/'chapter1/view/arc_contact_quality44.gdshader').open('x',encoding='utf-8') as output:output.write(source.rstrip()[:-1]+branch+'}\n')
print('Prepared arc contact; source43 fire/cold prefix retained')
