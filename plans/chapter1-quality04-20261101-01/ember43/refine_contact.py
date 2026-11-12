from pathlib import Path
import shutil

root=Path(__file__).resolve().parents[3]
backup=Path(__file__).resolve().parent/'proof/attempt01-source'
assert not backup.exists();backup.mkdir()
for name in ['chapter_elements_quality43.gd','ember_core_quality43.gdshader','ember_afterglow_quality43.gdshader']:
    shutil.copy2(Path('C:/Project/game-research/build-staging/ember43-preview01/chapter1/view')/name,backup/name)
source=(root/'chapter1/view/contact_quality10.gdshader').read_text(encoding='utf-8')
assert source.rstrip().endswith('}')
fire='''
 // Fire has a short directional spark, not two full-width white crossbars.
 // Cold/arc retain the existing branch above; the paid contact age is unchanged.
 if(data.g<.25){
  float spark=stroke(p*2.65,.026)*(1.-smoothstep(.02,.72,age));
  float hot=exp(-dot(p,p)*110.)*pow(1.-age,2.);
  float ember=exp(-dot(p,p)*35.)*pow(1.-age,1.6);
  ALBEDO=vec3(1.,.77,.34)*spark*fade*1.25+vec3(1.,.91,.62)*hot*1.4+vec3(.95,.17,.012)*ember*.40;
  ALPHA=clamp(spark*fade+hot+ember*.30,0.,1.);
 }
'''
destination=root/'chapter1/view/ember_contact_quality43.gdshader'
with destination.open('x',encoding='utf-8') as output:output.write(source.rstrip()[:-1]+fire+'}\n')
print('Prepared shorter fire contact; first trial source preserved')
