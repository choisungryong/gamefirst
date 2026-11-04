from pathlib import Path
BASE=Path('C:/Project/d2r-combat-baseline/chapter1/view')
SHADERS={
'comet.gdshader':r'''shader_type spatial;
render_mode unshaded, cull_disabled, blend_add, depth_draw_never, fog_disabled;
// Preserve instance scale when billboarding (Godot4.5 spatial shader built-ins).
// https://docs.godotengine.org/en/4.5/tutorials/shaders/shader_reference/spatial_shader.html
varying vec4 bolt_data;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+1.),f.x),f.y);}
void vertex(){
 bolt_data=INSTANCE_CUSTOM;
 vec3 scale=vec3(length(MODEL_MATRIX[0].xyz),length(MODEL_MATRIX[1].xyz),length(MODEL_MATRIX[2].xyz));VERTEX*=scale;
 float a=bolt_data.x*6.2831853-3.14159265;
 VERTEX.xy=mat2(vec2(cos(a),sin(a)),vec2(-sin(a),cos(a)))*VERTEX.xy;
 MODELVIEW_MATRIX=VIEW_MATRIX*mat4(INV_VIEW_MATRIX[0],INV_VIEW_MATRIX[1],INV_VIEW_MATRIX[2],MODEL_MATRIX[3]);
}
void fragment(){
 vec2 p=vec2((UV.x-.68)*2.,(UV.y-.5)*2.);
 float n=noise(vec2(p.x*9.-TIME*16.+bolt_data.w*7.,p.y*11.));
 float tip=exp(-dot(p*vec2(4.8,4.2),p*vec2(4.8,4.2)));
 float width=mix(.20,.36,bolt_data.z)*(1.-smoothstep(-.9,.4,p.x));
 float tail=(1.-smoothstep(width*.18,width,abs(p.y+sin(p.x*14.-TIME*23.)*.055)))*smoothstep(-1.42,-.7,p.x)*(1.-smoothstep(.08,.4,p.x));
 float shape=tail*(.40+n*.65)+tip*1.6;
 vec3 color=mix(vec3(.95,.075,.008),vec3(1.,.46,.035),clamp(n+tip*.5,0.,1.));
 vec3 core=vec3(1.,.86,.46)*tip*2.8;
 if(bolt_data.y>.3 && bolt_data.y<.8){
  float lance=1.-smoothstep(-.01,.025,abs(p.y)-max(0.,.14-abs(p.x+.12)*.24));
  float spine=(1.-smoothstep(.015,.045,abs(p.y)))*smoothstep(-1.15,-.85,p.x)*(1.-smoothstep(.18,.4,p.x));
  shape=lance*smoothstep(-1.15,-.82,p.x)*(1.-smoothstep(.25,.36,p.x));
  color=mix(vec3(.12,.53,.72),vec3(.70,.94,1.),spine);core=vec3(.70,.95,1.)*spine;
 }else if(bolt_data.y>.8){
  float shaft=(1.-smoothstep(.025,.06,abs(p.y)))*smoothstep(-.65,-.48,p.x)*(1.-smoothstep(.15,.27,p.x));
  float head=(1.-smoothstep(.0,.025,abs(p.y)-max(0.,.13-abs(p.x-.05)*.60)))*step(-.13,p.x)*step(p.x,.27);
  shape=max(shaft,head);color=vec3(.85,.16,.065);core=vec3(.32,.07,.025)*head;
 }
 ALBEDO=color*shape;EMISSION=(color*shape+core)*(1.5+bolt_data.z*.8);ALPHA=clamp(shape,0.,1.);
}
''',
'impact.gdshader':r'''shader_type spatial;
render_mode unshaded, cull_disabled, blend_add, depth_draw_never, fog_disabled;
varying vec4 impact_data;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+1.),f.x),f.y);}
void vertex(){impact_data=INSTANCE_CUSTOM;}
void fragment(){
 vec2 p=UV*2.-1.;float r=length(p);if(r>1.)discard;
 float age=impact_data.x,n=noise(p*6.-age*3.);
 float front=smoothstep(.08,.72,age)*(.85+n*.12);
 float heat=(1.-smoothstep(front-.26,front+.15,r))*(1.-age);
 float wave=exp(-pow((r-front)*12.,2.))*(.28+n*.6)*(1.-age);
 float core=exp(-r*7.)*pow(1.-age,3.);
 vec3 color=mix(vec3(.83,.045,.004),vec3(1.,.39,.018),n);
 float shape=heat*(.28+n*.5)+wave*.40;
 if(impact_data.y>.3 && impact_data.y<.8){
  float crystal=pow(abs(sin(atan(p.y,p.x)*6.+r*3.)),12.);
  shape=(wave*.55+crystal*heat*.5)*(1.-smoothstep(.7,1.,r));color=vec3(.25,.72,.95);
 }else if(impact_data.y>.8){
  float fissures=pow(abs(sin(atan(p.y,p.x)*9.+r*22.+n*3.)),18.);
  shape=(fissures*heat*.65+wave*.22);color=vec3(.46,.61,1.);
 }
 shape*=1.-smoothstep(.88,1.,r);
 ALBEDO=color*shape;EMISSION=color*shape*2.4+vec3(1.,.77,.30)*core*1.7;ALPHA=clamp(shape+core*.45,0.,1.);
}
''',
'flame_bloom.gdshader':r'''shader_type spatial;
render_mode unshaded, cull_disabled, blend_mix, depth_draw_never, fog_disabled;
varying vec4 bloom_data;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+1.),f.x),f.y);}
void vertex(){
 bloom_data=INSTANCE_CUSTOM;
 vec3 scale=vec3(length(MODEL_MATRIX[0].xyz),length(MODEL_MATRIX[1].xyz),length(MODEL_MATRIX[2].xyz));VERTEX*=scale;
 MODELVIEW_MATRIX=VIEW_MATRIX*mat4(INV_VIEW_MATRIX[0],INV_VIEW_MATRIX[1],INV_VIEW_MATRIX[2],MODEL_MATRIX[3]);
}
void fragment(){
 float age=bloom_data.x;vec2 p=UV*2.-1.;float n=noise(vec2(p.x*4.,p.y*5.+age*6.)+bloom_data.w*9.);
 float dome=1.-smoothstep(.52,.96,length(p*vec2(1.,.85)+vec2(0.,age*.35))+(n-.5)*.23);
 float fire=pow(1.-age,1.6)*(1.-smoothstep(-.4,.65,p.y+n*.35-age*.9));float heat=fire*dome;
 vec3 smoke=mix(vec3(.045,.038,.032),vec3(.13,.105,.08),n);
 ALBEDO=mix(smoke,vec3(1.,.20,.006),clamp(fire*1.7,0.,1.));
 EMISSION=vec3(1.,.36,.015)*heat*3.3+vec3(1.,.82,.36)*pow(heat,4.)*2.;ALPHA=dome*(1.-age)*.64;
}
''',
'element_particle.gdshader':r'''shader_type spatial;
render_mode unshaded, cull_disabled, blend_add, depth_draw_never;
void fragment(){ALBEDO=COLOR.rgb;EMISSION=COLOR.rgb*.85;ALPHA=COLOR.a;}
'''
}
for name,code in SHADERS.items():
    (BASE/name).write_text(code,encoding='utf-8')
print('Wrote',len(SHADERS),'assigned shaders')
