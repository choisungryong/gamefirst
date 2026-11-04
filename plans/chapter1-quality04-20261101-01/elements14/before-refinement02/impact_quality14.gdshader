shader_type spatial;
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
 vec3 core_color=vec3(1.,.77,.30);
 if(impact_data.y>.3 && impact_data.y<.8){
  float angle_=atan(p.y,p.x);
  float spokes=pow(abs(cos(angle_*6.+sin(r*11.)*.16)),34.);
  float broken=step(.24,noise(p*13.));
  float cracks=spokes*(1.-smoothstep(front-.12,front+.08,r))*smoothstep(.04,.16,r)*broken;
  shape=(wave*.42+cracks*.85)*pow(1.-age,.65);
  color=mix(vec3(.07,.35,.66),vec3(.62,.93,1.),cracks);
  core_color=vec3(.78,.96,1.);
 }else if(impact_data.y>.8){
  float fissures=pow(abs(sin(atan(p.y,p.x)*9.+r*22.+n*3.)),18.);
  shape=(fissures*heat*.65+wave*.22);color=vec3(.46,.61,1.);core_color=vec3(.80,.88,1.);
 }
 shape*=1.-smoothstep(.88,1.,r);
 ALBEDO=color*shape;EMISSION=color*shape*2.4+core_color*core*1.7;ALPHA=clamp(shape+core*.45,0.,1.);
}
